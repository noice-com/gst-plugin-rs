#!/usr/bin/env python3

# Parse Cargo.toml files for each plugin to collect their external dependencies.
# Meson will lookup those dependencies using pkg-config to be able to link
# static Rust plugins into gst-full.

from argparse import ArgumentParser
from pathlib import Path

try:
    # Python11 stdlib
    import tomllib
except ImportError:
    import tomli as tomllib


PARSER = ArgumentParser()
PARSER.add_argument('src_dir', type=Path)
PARSER.add_argument('plugins', nargs='*')


# Map plugin name to directory name, for those that does not match.
RENAMES = {
    'rsaudiofx': 'audiofx',
    'rsfile': 'file',
    'rsflv': 'flavors',
    'rstextwrap': 'wrap',
    'rsjson': 'json',
    'rsregex': 'regex',
    'rswebp': 'webp',
    'textahead': 'ahead',
    'rsonvif': 'onvif',
    'rstracers': 'tracers',
    'rsclosedcaption': 'closedcaption',
    'rsdav1d': 'dav1d',
    'webrtchttp': 'webrtc-http',
}


if __name__ == "__main__":
    opts = PARSER.parse_args()

    deps = set()
    for p in opts.plugins:
        assert p.startswith('gst')
        name = p[3:]
        name = RENAMES.get(name, name)
        files = list(opts.src_dir.glob(f'**/{name}/Cargo.toml'))
        assert len(files) == 1
        with files[0].open('rb') as f:
            data = tomllib.load(f)
            try:
                requires = data['package']['metadata']['capi']['pkg_config']['requires_private']
            except KeyError:
                continue
            deps.update([i.strip() for i in requires.split(',')])
    print(','.join(deps))
