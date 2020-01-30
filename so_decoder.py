import json
import argparse
import os


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('file', action='store',
                        help='saved objects file to parse')
    parser.add_argument('out', action='store',
                        help='directory to write output files')
    return parser.parse_args()


def decode_json(saved_obj):
    for key, val in saved_obj.items():
        if isinstance(val, dict):
            decode_json(val)
        if 'JSON' in key or 'visState' in key:
            saved_obj[key] = json.loads(val)

    return saved_obj


def parse_json_line(output, data):
    data_id = data['id']
    data_type = data['type']
    output[data_type][data_id] = {
        'title': data['attributes']['title'],
        'data': decode_json(data)
    }


def main():
    args = parse_args()
    output = {}
    dirs_to_make = ['index-pattern', 'visualization', 'dashboard', 'search', 'map']
    for name in dirs_to_make:
        os.makedirs(os.path.join(args.out, name), exist_ok=True)
        output.setdefault(name, {})

    with open(args.file, 'r') as f:
        lines = f.readlines()
        for line in lines:
            data = json.loads(line)
            if 'exportedCount' in data:
                continue
            parse_json_line(output, data)

    for vis_type, ids in output.items():
        for vis_id, vis_info in ids.items():
            if vis_type == 'index-pattern':
                name = vis_info['title']
            else:
                name = vis_id
            with open(os.path.join(args.out, vis_type, '{}.json'.format(name)), 'w') as write_file:
                json.dump(vis_info['data'], write_file, indent=4)


if __name__ == '__main__':
    main()
