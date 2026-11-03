import gzip
import os

from doc_compressor import choose_poser_docs, POSER_EXTENSIONS

if __name__ == '__main__':

    # reverse POSER_EXTENSIONS
    ps_extensions = {}
    for ext_src, ext_zip in POSER_EXTENSIONS.items():
        ps_extensions[ext_zip] = ext_src

    count = 0
    for compressed_path in choose_poser_docs(list(ps_extensions.keys()))[1]:
        data = gzip.open(compressed_path, 'rb').read().decode()
        path_no_ext, ext = compressed_path.rsplit('.', 1)
        date_modified = os.path.getmtime(compressed_path)
        decompressed_path = path_no_ext + '.' + ps_extensions[ext]
        open(decompressed_path, 'w').write(data)
        os.utime(decompressed_path, (date_modified, date_modified))
        os.remove(compressed_path)
        count += 1
    if count > 0:
        print(f'{count} files were decompressed.')
