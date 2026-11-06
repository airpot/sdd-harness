"""Check the supported JUnit report profile for one strict gate."""
from collections import Counter
import os
import re
from xml.etree import ElementTree as ET


MAX_REPORT_BYTES = 8 * 1024 * 1024


class ReportTree(ET.TreeBuilder):
    def doctype(self, name, public_id, system_id):
        raise ValueError('Do not use document type or entity declarations in JUnit reports')


def case_key(case):
    return tuple(case[key] for key in ('shard', 'file', 'classname', 'name'))


def validate_cases(gate):
    cases = gate.get('junit')
    if not isinstance(cases, dict) or set(cases) != set(gate['tests']):
        raise ValueError('Give one JUnit selector for each mandatory test ID')
    for case in cases.values():
        if not isinstance(case, dict) or set(case) != {'shard', 'file', 'classname', 'name'} or any(
                not isinstance(value, str) or not value.strip() or len(value) > 1024 or
                any(ord(char) < 32 for char in value) for value in case.values()):
            raise ValueError('Each selector needs a shard, file, class, and exact name')
        if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_-]{0,63}', case['shard']):
            raise ValueError('Use a short report shard identifier')
        file = case['file']
        if ':' in file or '\\' in file or any(part in ('', '.', '..') for part in file.split('/')):
            raise ValueError('Use a project-relative JUnit file path with forward slashes')
    if len({case_key(case) for case in cases.values()}) != len(cases):
        raise ValueError('JUnit selectors must be unique')
    names = shards(gate)
    if len({name.lower() for name in names}) != len(names) or any(
            re.fullmatch(r'(?i:CON|PRN|AUX|NUL|COM[1-9]|LPT[1-9])', name) for name in names):
        raise ValueError('Use shard names that identify distinct regular files on all supported systems')


def shards(gate):
    return sorted({case['shard'] for case in gate['junit'].values()})


def read_report(path):
    with path.open('rb') as stream:
        raw = stream.read(MAX_REPORT_BYTES + 1)
    if len(raw) > MAX_REPORT_BYTES:
        raise ValueError('The report is larger than the report limit')
    return raw


def check_counts(element, tests, skipped):
    for key, expected in (('tests', tests), ('skipped', skipped), ('failures', 0), ('errors', 0)):
        if key in element.attrib and element.get(key) != str(expected):
            raise ValueError('The JUnit report has a conflicting ' + key + ' count')


def check_children(element, allowed, cases=False):
    for child in element:
        if child.tag not in allowed:
            raise ValueError('The JUnit report contains an unsupported result entry')
        if child.tag == 'properties':
            if any(prop.tag != 'property' or len(prop) for prop in child):
                raise ValueError('The JUnit report contains an unsupported property entry')
        elif not (cases and child.tag == 'testcase') and len(child):
            raise ValueError('The JUnit report contains an unexpected nested result')


def check_report(raw, run_id, shard, cases):
    source = raw.decode('utf-8-sig')
    declared = re.match(r'''<\?xml\s[^?]*\bencoding\s*=\s*(['"])([^'"]+)\1''', source)
    if '\x00' in source or (declared and declared[2].lower() != 'utf-8'):
        raise ValueError('The JUnit report must use UTF-8')
    try:
        root = ET.fromstring(source, parser=ET.XMLParser(target=ReportTree()))
    except ET.ParseError as exc:
        raise ValueError('The JUnit report is not valid XML') from exc
    suites = [root] if root.tag == 'testsuite' else list(root) if root.tag == 'testsuites' else []
    if not suites or any(suite.tag != 'testsuite' for suite in suites):
        raise ValueError('The JUnit report must contain one or more flat test suites')
    counts = Counter()
    skipped = set()
    total_tests = total_skips = 0
    for suite in suites:
        for name, value in (('sdd.run_id', run_id), ('sdd.shard', shard)):
            entries = [prop.get('value') for prop in suite.findall('./properties/property')
                       if prop.get('name') == name]
            if entries != [value]:
                raise ValueError('The JUnit report does not identify this run and shard')
        check_children(suite, ('properties', 'testcase', 'system-out', 'system-err'), cases=True)
        tests = suite.findall('testcase')
        skips = 0
        for test in tests:
            file = test.get('file', '')
            if os.name == 'nt':
                file = file.replace('\\', '/')
            key = (shard, file, test.get('classname'), test.get('name'))
            if test.get('status', 'run') not in ('run', 'passed'):
                raise ValueError('The JUnit report contains a failed, unstable, or unsupported test result')
            check_children(test, ('properties', 'system-out', 'system-err', 'skipped'))
            counts[key] += 1
            if test.find('skipped') is not None:
                skipped.add(key)
                skips += 1
        check_counts(suite, len(tests), skips)
        total_tests += len(tests)
        total_skips += skips
    if root.tag == 'testsuites':
        check_counts(root, total_tests, total_skips)
    for test_id, case in cases.items():
        key = case_key(case)
        if case['shard'] == shard and (counts[key] != 1 or key in skipped):
            raise ValueError('The mandatory JUnit case is missing, skipped, or repeated: ' + test_id)
