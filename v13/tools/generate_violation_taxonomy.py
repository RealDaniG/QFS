import re
import json
import os
import sys
from datetime import datetime, timezone

def parse_violation_line(line):
    """
    Parse line format:
    v13/services/notification_service.py:96 [NONDETERMINISTIC_ITERATION] Dict/set iteration must use sorted()
    """
    pattern = '^\\s*([^:]+):(\\d+)\\s+\\[([^\\]]+)\\]\\s+(.+)$'
    match = re.match(pattern, line.strip())
    if match:
        return {'file': match.group(1), 'line': int(match.group(2)), 'type': match.group(3), 'message': match.group(4)}
    return None

def classify_complexity(violation_type, code_context=''):
    """
    Determine fix complexity.
    """
    complexity_map = {'FORBIDDEN_CALL': 'trivial' if 'print' in code_context else 'low', 'NONDETERMINISTIC_ITERATION': 'medium', 'FORBIDDEN_CONTAINER': 'low', 'FORBIDDEN_TYPE': 'medium', 'GLOBAL_MUTATION': 'high', 'FLOAT_LITERAL': 'critical', 'FORBIDDEN_COMP': 'medium'}
    return complexity_map.get(violation_type, 'medium')

def is_auto_fixable(violation_type, code_context, file_path):
    """
    Determine if violation can be safely auto-fixed
    """
    if violation_type == 'FORBIDDEN_CALL' and 'print' in code_context:
        if '/tools/' in file_path or '/tests/' in file_path or '\\tools\\' in file_path or ('\\tests\\' in file_path):
            return True
    if violation_type == 'NONDETERMINISTIC_ITERATION':
        if 'for' in code_context and 'in' in code_context:
            return True
    if violation_type == 'FORBIDDEN_CONTAINER':
        if '{' in code_context and '}' in code_context:
            return True
    return False

def generate_fix_batches(all_violations):
    """
    Generate prioritized fix batches based on violation analysis.
    """
    batches = []
    print_violations = [v for v in all_violations if v['type'] == 'FORBIDDEN_CALL' and 'print' in v.get('code', '')]
    if print_violations:
        batches.append({'batch_id': 1, 'name': 'print_statement_removal', 'category': 'FORBIDDEN_CALL', 'violations': len(print_violations), 'complexity': 'trivial', 'auto_fix_confidence': 0.99, 'estimated_time_minutes': max(5, int(len(print_violations) * 0.1)), 'risk': 'minimal', 'files': list(set((v['file'] for v in print_violations))), 'transformation': 'Remove print() or replace with logger.info()', 'validation': 'Verify no print() in non-test core logic'})
    dict_keys_violations = [v for v in all_violations if v['type'] == 'NONDETERMINISTIC_ITERATION' and '.keys()' in v.get('code', '')]
    if dict_keys_violations:
        batches.append({'batch_id': 2, 'name': 'sorted_iterations_simple', 'category': 'NONDETERMINISTIC_ITERATION', 'violations': len(dict_keys_violations), 'complexity': 'low', 'auto_fix_confidence': 0.9, 'estimated_time_minutes': max(10, int(len(dict_keys_violations) * 0.2)), 'risk': 'low', 'pattern': 'for x in dict.keys():', 'transformation': 'for x in sorted(dict.keys()):', 'validation': "Ensure iteration order doesn't break logic"})
    set_violations = [v for v in all_violations if v['type'] == 'FORBIDDEN_CONTAINER']
    if set_violations:
        batches.append({'batch_id': 3, 'name': 'set_to_list_conversion', 'category': 'FORBIDDEN_CONTAINER', 'violations': len(set_violations), 'complexity': 'low', 'auto_fix_confidence': 0.85, 'estimated_time_minutes': max(10, int(len(set_violations) * 0.1)), 'risk': 'low', 'transformation': 'Replace {"A", "B"} with ["A", "B"]', 'validation': 'Verify membership tests still work'})
    other_iter_violations = [v for v in all_violations if v['type'] == 'NONDETERMINISTIC_ITERATION' and v not in dict_keys_violations]
    if other_iter_violations:
        batches.append({'batch_id': 4, 'name': 'sorted_iterations_complex', 'category': 'NONDETERMINISTIC_ITERATION', 'violations': len(other_iter_violations), 'complexity': 'medium', 'auto_fix_confidence': 0.75, 'estimated_time_minutes': max(20, int(len(other_iter_violations) * 0.5)), 'risk': 'medium', 'pattern': 'for obj in collection:', 'transformation': 'for obj in sorted(collection, key=lambda x: (x.timestamp, x.id)):', 'validation': 'Verify key function matches business logic', 'requires_testing': True})
    global_violations = [v for v in all_violations if v['type'] == 'GLOBAL_MUTATION']
    if global_violations:
        batches.append({'batch_id': 5, 'name': 'global_mutation_refactor', 'category': 'GLOBAL_MUTATION', 'violations': len(global_violations), 'complexity': 'high', 'auto_fix_confidence': 0.4, 'estimated_time_minutes': max(60, int(len(global_violations) * 2)), 'risk': 'high', 'transformation': 'Move module state to function/class scope', 'validation': 'Run full test suite after each refactor', 'requires_manual_review': True})
    float_violations = [v for v in all_violations if v['type'] == 'FLOAT_LITERAL']
    if float_violations:
        batches.append({'batch_id': 6, 'name': 'float_to_bignum_economics', 'category': 'FLOAT_LITERAL', 'violations': len(float_violations), 'complexity': 'critical', 'auto_fix_confidence': 0.3, 'estimated_time_minutes': max(120, int(len(float_violations) * 3)), 'risk': 'critical', 'transformation': 'Replace floats with BigNum128.from_string()', 'validation': 'Verify economic invariants preserved', 'requires_manual_review': True, 'requires_precision_analysis': True})
    return batches

def main():
    input_file = 'zero_sim_violations_raw.txt'
    if not os.path.exists(input_file):
        sys.exit(1)
    all_violations = []
    with open(input_file, 'r', encoding='utf-8', errors='ignore') as f:
        lines = f.readlines()
    current_file_lines = {}
    for line in lines:
        v_data = parse_violation_line(line)
        if v_data:
            file_path = v_data['file']
            code_context = ''
            real_path = file_path
            if not os.path.exists(real_path):
                pass
            if real_path not in current_file_lines and os.path.exists(real_path):
                try:
                    with open(real_path, 'r', encoding='utf-8', errors='ignore') as code_f:
                        current_file_lines[real_path] = code_f.readlines()
                except:
                    current_file_lines[real_path] = []
            if real_path in current_file_lines:
                file_content = current_file_lines[real_path]
                if 0 <= v_data['line'] - 1 < len(file_content):
                    code_context = file_content[v_data['line'] - 1].strip()
            v_data['code'] = code_context
            v_data['complexity'] = classify_complexity(v_data['type'], code_context)
            v_data['auto_fixable'] = is_auto_fixable(v_data['type'], code_context, v_data['file'])
            all_violations.append(v_data)
        elif line.strip().startswith('>') and all_violations:
            prev_violation = all_violations[-1]
            if not prev_violation.get('code'):
                prev_violation['code'] = line.strip().lstrip('>').strip()
                prev_violation['complexity'] = classify_complexity(prev_violation['type'], prev_violation['code'])
                prev_violation['auto_fixable'] = is_auto_fixable(prev_violation['type'], prev_violation['code'], prev_violation['file'])
    violations_by_category = {}
    violations_by_file = {}
    for v in all_violations:
        cat = v['type']
        violations_by_category[cat] = violations_by_category.get(cat, 0) + 1
        fpath = v['file']
        if fpath not in violations_by_file:
            violations_by_file[fpath] = {'total_violations': 0, 'violations': []}
        violations_by_file[fpath]['total_violations'] += 1
        violations_by_file[fpath]['violations'].append({'line': v['line'], 'type': v['type'], 'code': v.get('code', ''), 'message': v['message'], 'complexity': v['complexity'], 'auto_fixable': v['auto_fixable']})
    structured_data = {'scan_metadata': {'timestamp': datetime.now(timezone.utc).isoformat(), 'total_violations': len(all_violations), 'files_affected': len(violations_by_file), 'scanner_version': 'v13/libs/AST_ZeroSimChecker.py'}, 'violations_by_category': violations_by_category, 'violations_by_file': violations_by_file, 'priority_batches': {}}
    fix_batches = generate_fix_batches(all_violations)
    priority_batches_map = {}
    for batch in fix_batches:
        priority_batches_map[f"batch_{batch['batch_id']}_{batch['name']}"] = {'category': batch['category'], 'estimated_violations': batch['violations'], 'complexity': batch['complexity'], 'auto_fix_confidence': batch['auto_fix_confidence'], 'files': list(batch.get('files', []))[:5]}
    structured_data['priority_batches'] = priority_batches_map
    with open('zero_sim_violations_structured.json', 'w') as f:
        json.dump(structured_data, f, indent=2)
    fix_plan = {'fix_batches': fix_batches}
    with open('zero_sim_fix_plan.json', 'w') as f:
        json.dump(fix_plan, f, indent=2)
    manual_review_items = [v for v in all_violations if not v['auto_fixable'] or v['complexity'] in ['high', 'critical']]
    with open('zero_sim_manual_review.md', 'w') as f:
        f.write('# Zero-Sim Manual Review Queue\n\n')
        f.write(f'Total items requiring manual review: {len(manual_review_items)}\n\n')
        by_type = {}
        for v in manual_review_items:
            by_type.setdefault(v['type'], []).append(v)
        for vtype, items in sorted(by_type.items()):
            f.write(f'## {vtype} ({len(items)})\n')
            for item in items[:20]:
                f.write(f"- **{item['file']}:{item['line']}**\n")
                f.write(f"  - Code: `{item.get('code', 'N/A').strip()}`\n")
                f.write(f"  - Reasoning: {item['message']}\n\n")
            if len(items) > 20:
                f.write(f'  - ... and {len(items) - 20} more\n\n')
    stats = {'total_violations': len(all_violations), 'breakdown_by_category': violations_by_category, 'top_offending_files': sorted([{'file': k, 'count': v['total_violations']} for k, v in sorted(violations_by_file.items())], key=lambda x: x['count'], reverse=True)[:10]}
    with open('zero_sim_statistics.json', 'w') as f:
        json.dump(stats, f, indent=2)
    with open('zero_sim_phase3_ready.flag', 'w') as f:
        f.write(f'Phase 2 Complete. {len(all_violations)} violations cataloged.')
if __name__ == '__main__':
    main()