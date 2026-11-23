#!/usr/bin/env python3
"""Start a Windows generator without write access to the acceptance paths."""

import argparse
from contextlib import ExitStack
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time


LOW, MEDIUM = "S-1-16-4096", "S-1-16-8192"


def existing_path(value):
    path = Path(os.path.abspath(value))
    for part in (path, *path.parents):
        if part.lstat().st_file_attributes & 0x400:
            raise ValueError(f"A path component is a reparse point: {part}")
    return path


def label(path, security):
    acl = security.GetNamedSecurityInfo(
        str(path), security.SE_FILE_OBJECT, security.LABEL_SECURITY_INFORMATION,
    ).GetSecurityDescriptorSacl()
    labels = []
    if acl is not None:
        for index in range(acl.GetAceCount()):
            (kind, _), mask, sid = acl.GetAce(index)
            if kind == 17:  # SYSTEM_MANDATORY_LABEL_ACE_TYPE
                labels.append((security.ConvertSidToStringSid(sid), mask))
    if len(labels) > 1:
        raise ValueError(f"The path has more than one integrity label: {path}")
    return labels[0] if labels else (MEDIUM, 1)  # Windows default: NO_WRITE_UP.


def run(protected, timeout, argv):
    if os.name != "nt":
        raise ValueError("This launcher requires Windows. Use a separate trusted verifier on this host.")
    import win32api
    import win32con
    import win32event
    import win32file
    import win32job
    import win32process
    import win32security as security

    app = Path(argv[0])
    if not app.is_absolute() or not app.is_file() or app.suffix.lower() != ".exe":
        raise ValueError("Use the absolute path of a Windows executable.")
    checked, volumes = set(), set()

    def check_volume(path):
        volume = path.anchor
        if volume not in volumes:
            if (win32file.GetDriveType(volume) != win32con.DRIVE_FIXED
                    or win32api.GetVolumeInformation(volume)[-1].upper() != "NTFS"):
                raise ValueError(f"The launcher requires a local NTFS path: {path}")
            volumes.add(volume)

    for value in protected:
        path = existing_path(value)
        check_volume(path)
        for part in (path, *path.parents):
            if part not in checked:
                sid, policy = label(part, security)
                if int(sid.rsplit("-", 1)[-1]) < 8192 or not policy & 1:
                    raise ValueError(f"The path is not protected against low integrity writes: {part}")
                checked.add(part)
    local_low = existing_path(Path(os.environ["LOCALAPPDATA"]).parent / "LocalLow")
    check_volume(local_low)
    if not local_low.is_dir() or label(local_low, security)[0] != LOW:
        raise ValueError("The user's LocalLow directory does not have a low integrity label.")

    with ExitStack() as handles:
        def keep(handle):
            handles.callback(handle.Close)
            return handle

        parent = keep(security.OpenProcessToken(win32api.GetCurrentProcess(), win32con.TOKEN_ALL_ACCESS))
        sid, _ = security.GetTokenInformation(parent, security.TokenIntegrityLevel)
        if security.ConvertSidToStringSid(sid) != MEDIUM:
            raise ValueError("Start this launcher from a trusted, medium integrity process.")
        child = keep(security.CreateRestrictedToken(parent, security.DISABLE_MAX_PRIVILEGE, (), (), ()))
        security.SetTokenInformation(child, security.TokenIntegrityLevel,
                                     (security.ConvertStringSidToSid(LOW), security.SE_GROUP_INTEGRITY))
        sid, _ = security.GetTokenInformation(child, security.TokenIntegrityLevel)
        if security.ConvertSidToStringSid(sid) != LOW:
            raise ValueError("The generator token does not have low integrity.")
        scratch = Path(tempfile.mkdtemp(prefix="sdd-generator-", dir=local_low))
        if label(scratch, security)[0] != LOW:
            raise ValueError(f"The generator directory does not have low integrity: {scratch}")
        env = {"SystemRoot": os.environ["SystemRoot"], "APPDATA": os.environ["APPDATA"],
               "TEMP": str(scratch), "TMP": str(scratch)}
        env.update({key: value for key, value in os.environ.items() if key.startswith("GIT_")})
        flags = win32con.CREATE_UNICODE_ENVIRONMENT | win32con.CREATE_SUSPENDED | subprocess.CREATE_NO_WINDOW
        job = keep(win32job.CreateJobObject(None, ""))
        limits = win32job.QueryInformationJobObject(job, win32job.JobObjectExtendedLimitInformation)
        limits["BasicLimitInformation"]["LimitFlags"] |= win32job.JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE
        win32job.SetInformationJobObject(job, win32job.JobObjectExtendedLimitInformation, limits)
        proc, thread, pid, _ = win32process.CreateProcessAsUser(
            child, str(app), subprocess.list2cmdline(argv), None, None, False, flags,
            env, str(scratch), win32process.STARTUPINFO(),
        )
        keep(proc)
        keep(thread)
        try:
            win32job.AssignProcessToJobObject(job, proc)
        except Exception:
            win32process.TerminateProcess(proc, 1)
            raise
        win32process.ResumeThread(thread)
        wait = win32event.WaitForSingleObject(proc, timeout * 1000)
        timed_out = wait == win32event.WAIT_TIMEOUT
        if not timed_out and wait != win32event.WAIT_OBJECT_0:
            raise ValueError("The generator wait did not return a completion result.")
        status = 124 if timed_out else win32process.GetExitCodeProcess(proc)
        win32job.TerminateJobObject(job, 124 if timed_out else 1)
        deadline = time.monotonic() + 5
        while win32job.QueryInformationJobObject(job, win32job.JobObjectBasicAccountingInformation)["ActiveProcesses"]:
            if time.monotonic() >= deadline:
                raise TimeoutError("The generator job still has active processes.")
            time.sleep(0.05)
        return {"scratch": str(scratch), "generator_integrity_sid": LOW,
                "generator_pid": pid, "generator_exit": status, "timed_out": timed_out,
                "inherited_handles": False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--protect", action="append", required=True, metavar="PATH",
                        help="existing trusted file or directory; repeat for each path")
    parser.add_argument("--timeout", type=int, default=600, metavar="SECONDS")
    parser.add_argument("command", nargs=argparse.REMAINDER, help="-- ABSOLUTE_EXE [ARG ...]")
    args = parser.parse_args()
    argv = args.command[1:] if args.command[:1] == ["--"] else args.command
    if not argv or not 1 <= args.timeout <= 86400:
        parser.error("Use an executable and a timeout from 1 to 86400 seconds.")
    try:
        result = run(args.protect, args.timeout, argv)
    except ImportError:
        parser.exit(2, "Generator isolation needs pywin32 for this Python on Windows.\n")
    except Exception as exc:
        parser.exit(2, f"Generator isolation failed: {exc}\n")
    print(json.dumps(result))
    return result["generator_exit"]


if __name__ == "__main__":
    sys.exit(main())
