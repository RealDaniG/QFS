import os

def fix_drv_packet():
    file_path = 'v13/core/DRV_Packet.py'
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    new_lines = []
    state = 'NORMAL'
    for line in lines:
        stripped = line.strip()
        if stripped.startswith('<<<<<<< HEAD'):
            state = 'HEAD_BLOCK'
            continue
        elif stripped.startswith('======='):
            if state == 'HEAD_BLOCK':
                state = 'IGNORE_BLOCK'
            elif state == 'NORMAL':
                pass
            continue
        elif stripped.startswith('>>>>>>>'):
            if state == 'IGNORE_BLOCK':
                state = 'NORMAL'
            elif state == 'HEAD_BLOCK':
                state = 'NORMAL'
            continue
        if state == 'NORMAL':
            new_lines.append(line)
        elif state == 'HEAD_BLOCK':
            new_lines.append(line)
        elif state == 'IGNORE_BLOCK':
            pass
    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
if __name__ == '__main__':
    fix_drv_packet()