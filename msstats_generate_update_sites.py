#!/usr/bin/env python3
import sys
import argparse
import os
import requests
import shutil
from os.path import join
import subprocess

# Constants
copyright = """Copyright The OpenMS Team -- Eberhard Karls University Tuebingen,
ETH Zurich, and Freie Universitaet Berlin 2002-2013.
"""
splash = "https://raw.githubusercontent.com/genericworkflownodes/GenericKnimeNodes/develop/com.genericworkflownodes.knime.node_generator/sample-openms/icons/splash.png"
category = "https://raw.githubusercontent.com/genericworkflownodes/GenericKnimeNodes/develop/com.genericworkflownodes.knime.node_generator/sample-openms/icons/category.png"


licence = """--------------------------------------------------------------------------
                  OpenMS -- Open-Source Mass Spectrometry
--------------------------------------------------------------------------
Copyright The OpenMS Team -- Eberhard Karls University Tuebingen,
ETH Zurich, and Freie Universitaet Berlin 2002-2012.

This software is released under a three-clause BSD license:
 * Redistributions of source code must retain the above copyright
   notice, this list of conditions and the following disclaimer.
 * Redistributions in binary form must reproduce the above copyright
   notice, this list of conditions and the following disclaimer in the
   documentation and/or other materials provided with the distribution.
 * Neither the name of any author or any participating institution
   may be used to endorse or promote products derived from this software
   without specific prior written permission.
For a full list of authors, refer to the file AUTHORS.
--------------------------------------------------------------------------
THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
ARE DISCLAIMED. IN NO EVENT SHALL ANY OF THE AUTHORS OR THE CONTRIBUTING
INSTITUTIONS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS;
OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR
OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF
ADVISED OF THE POSSIBILITY OF SUCH DAMAGE."""

description = """OpenMS is an open-source software C++ library for LC/MS data management and
analyses. It offers an infrastructure for the development of mass
spectrometry related software and powerful 2D and 3D visualization.

OpenMS is free software available under the three clause BSD license and runs
under Windows, MacOSX and Linux."""


plugin_properties = """# the name of the plugin
pluginPackage=de.msstatsconverter

# the name of the plugin
pluginName=MSstatsConverter

# the version of the plugin
pluginVersion=1

# the path (starting from KNIMEs Community Nodes node)
nodeRepositoyRoot=community

executor=com.genericworkflownodes.knime.execution.impl.LocalToolExecutor
commandGenerator=com.genericworkflownodes.knime.execution.impl.OpenMSCommandGenerator
"""
binaries_ini = """LD_LIBRARY_PATH=$ROOT/lib/
DATA_PATH=$ROOT/data/
"""



def create_plugin_directory_structure(input_dir, target):
    required_dirs = ['descriptors', 'icons', 'payload']
    os.mkdir(target)
    for required_dir in required_dirs:
        os.mkdir(os.path.join(target, required_dir))
    with open(os.path.join(target, "COPYRIGHT"), 'w') as f:
        f.write(copyright)
    with open(os.path.join(target, "DESCRIPTION"), 'w') as f:
        f.write(description)
    with open(os.path.join(target, "LICENSE"), 'w') as f:
        f.write(licence)
    with open(os.path.join(target, "plugin.properties"), 'w') as f:
        f.write(plugin_properties)

    r_splash = requests.get(splash)
    r_category = requests.get(category)

    with open(os.path.join(target, 'icons', 'splash.png'), 'wb') as f:
        for chunk in r_splash.iter_content():
            f.write(chunk)
    with open(os.path.join(target, 'icons', 'category.png'), 'wb') as f:
        for chunk in r_category.iter_content():
            f.write(chunk)
    lib_dir = 'lib'
    bin_dir = 'bin'

    # generate the payloads
    payload = join(target, 'payload', 'binaries_lnx_64')
    os.mkdir(payload)
    for payload_dir in [bin_dir, 'data']:
        os.mkdir(os.path.join(payload, payload_dir))

    # Copy the MSstatsConverterBinary
    mstats_converter_binary = join(input_dir, bin_dir, 'MSstatsConverter')

    # Execute the binary to write the CTD file
    subprocess.Popen([mstats_converter_binary,
                      '-write_ctd',
                      join(target, 'descriptors')]).communicate()

    shutil.copy(mstats_converter_binary,
                join(payload, bin_dir, 'MSstatsConverter'))
    # Copy library recursively
    shutil.copytree(join(input_dir, lib_dir),
                    join(payload, lib_dir))
    with open(join(payload, 'binaries.ini'), 'w') as f:
        f.write(binaries_ini)
    # Create the zipfile
    shutil.make_archive(join(target, 'payload', 'binaries_lnx_64'),
                        'zip',
                        payload)
    shutil.rmtree(payload)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', type=str, required=True)
    parser.add_argument('-o', type=str, required=True)
    args = parser.parse_args(sys.argv[1:])

    if os.path.exists(args.o):
        print("FATAL: Output path already exists. Cannot continue!",
              file=sys.stdout)
        sys.exit(1)
    if not os.path.isdir(args.i):
        print("FATAL: Input path is not a directory. Cannot continue!",
              file=sys.stdout)
        sys.exit(2)
    create_plugin_directory_structure(args.i, args.o)



if __name__ == '__main__':
    main()
