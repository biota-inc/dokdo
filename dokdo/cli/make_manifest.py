import os
import re
from pathlib import Path

def get_sample_id(filename):
    """
    ファイル名から拡張子や末尾の _R1_001 / _R2_001,
    さらにオプションの _L<数字>, _S<数字> を取り除き，
    残った文字列をサンプルIDとして返す．
    """
    # 拡張子(.fastq / .fastq.gz / .fq / .fq.gz)を除去
    basename = re.sub(r'\.(?:fastq|fq)(?:\.gz)?$', '', filename)

    # 末尾の '_R1_001' または '_R2_001' を除去
    basename = re.sub(r'_R[12]_001$', '', basename)

    # オプションの '_L<数字>' があれば除去 (例: _L001)
    basename = re.sub(r'_L\d+$', '', basename)

    # オプションの '_S<数字>' があれば除去 (例: _S23)
    basename = re.sub(r'_S\d+$', '', basename)

    return basename

def make_manifest(fastq_dir, output_file):
    """
    ディレクトリに含まれるFASTQファイルからマニフェスト(tsv)を作成する．
    Undeterminedが含まれるファイルは除外する．
    """
    fastq_dir = Path(fastq_dir).resolve()
    files = {}

    for r, d, f in os.walk(fastq_dir):
        for x in f:
            # Undeterminedを含むファイルは除外
            if 'Undetermined' in x:
                continue

            # サンプルIDを取得
            name = get_sample_id(x)

            # R1 / R2 に応じて辞書に格納
            if '_R1_001.fastq' in x:
                if name not in files:
                    files[name] = ['', '']
                files[name][0] = f"{r}/{x}"
            elif '_R2_001.fastq' in x:
                if name not in files:
                    files[name] = ['', '']
                files[name][1] = f"{r}/{x}"
            else:
                # それ以外は特に処理しない
                pass

    # ファイル書き込み
    with open(output_file, 'w') as of:
        headers = ['sample-id', 'forward-absolute-filepath', 'reverse-absolute-filepath']
        of.write('\t'.join(headers) + '\n')

        for name in sorted(files):
            fields = [name, files[name][0], files[name][1]]
            of.write('\t'.join(fields) + '\n')
