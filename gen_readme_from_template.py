import argparse
import io
import json


def write_img_sect(d: dict, f: io.TextIOWrapper, s_id: str):
    # ![<ALT TEXT>](<FILEPATH>)
    if 'src' not in d.keys():
        raise Exception(f'Missing "src" field in {s_id}')
    if 'alt' not in d.keys():
        d['alt'] = ""

    f.write(f'![{d["alt"]}]({d["src"]})\n\n')


def write_bgl_sect(d: dict, f: io.TextIOWrapper, s_id: str):
    # [![<TEXT>](https://img.shields.io/badge/<TEXT>-<COLOR>?style=for-the-badge&logo=<LOGO_ID>&logoColor=white&link=<LINK>)](<LINK>)
    if 'badges' not in d.keys():
        raise Exception(f'Missing "badges" field in {s_id}')

    for b in d['badges']:
        if len(b) != 4:
            raise Exception(f'{b} must be of length 4')

        f.write(f'[![{b[0]}](https://img.shields.io/badge/{b[0].replace(" ", "_")}-{b[1][1:]}?style=for-the-badge&logo={b[2]}&logoColor=white&link={b[3]})]({b[3]})\n')
    f.write('\n')


tbl_txt_writer = lambda x: ' ' + x + ' '
make_bgr_string = lambda x: ''.join(f'![{b[0]}](https://img.shields.io/badge/{b[0].replace(" ", "_")}-{b[1][1:]}?style=for-the-badge&logo={b[2]}&logoColor={"white" if len(b) < 4 else b[3]})' for b in x)
tbl_bdg_grp_writer = lambda x: ' ' + make_bgr_string(x) + ' '


TABLE_WRITERS = {
    'text': tbl_txt_writer,
    'badge_group': tbl_bdg_grp_writer
}


def write_tbl_sect(d: dict, f: io.TextIOWrapper, s_id: str):
    if 'col_types' not in d.keys():
        raise Exception(f'Missing "col_types" field in {s_id}')
    if 'rows' not in d.keys():
        raise Exception(f'Missing "rows" field in {s_id}')

    tbl_width = len(d['col_types'])

    if 'cols' in d.keys():   
        if len(d['cols']) != tbl_width:
            raise Exception('"cols" and "col_types" values must have identical length')

        # write header - | Type | Skills |
        f.write('| ' + ' | '.join(d['cols']) + ' |\n')

    # write top of table - | :------------- | :------------- |
    f.write('|' + '|'.join([' :------------- ' for _ in range(tbl_width)]) + '|\n')

    col_types = d['col_types']
    
    # write rows
    # | Programming Languages | ![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black) |
    for r in d['rows']:
        f.write('|' + '|'.join(TABLE_WRITERS[t](v) for t, v in zip(col_types, r)) + '|\n')
    
    f.write('\n')


def write_blt_sect(d: dict, f: io.TextIOWrapper, s_id: str):
    if 'items' not in d.keys():
        raise Exception(f'Missing "src" field in {s_id}')

    for i in d['items']:
        f.write(f'- {i}\n')

    f.write(f'\n')


SECTION_WRITERS = {
    'image': write_img_sect,
    'badge_group_linked': write_bgl_sect,
    'table': write_tbl_sect,
    'bullets': write_blt_sect
}


def write_to_readme(data: dict, f: io.TextIOWrapper):
    for s_id, section in sorted(data.items(), key=lambda x: x[0]):
        if 'title' in section.keys():
            f.write(f'# {section["title"]}\n\n')

        if 'format' in section.keys() and section['format'] in SECTION_WRITERS.keys():
            SECTION_WRITERS[section['format']](section, f, s_id)
        else:
            raise Exception(f'Format field for {s_id} is missing or invalid')


def main():
    # ARGUMENTS
    parser = argparse.ArgumentParser(description='Generate a README resume for your GitHub profile page')
    parser.add_argument('--template', default='template.json', type=str, help='Path for the template file; "template.json" by default')
    parser.add_argument('--outfile', default='generated_readme.md', type=str, help='File path to write output to; "README.md" by default')
    args = parser.parse_args()

    with open(args.outfile, 'w') as f:
        data = json.load(open(args.template, 'r'))
        write_to_readme(data, f)

    print('DONE')


if __name__ == '__main__':
    main()
