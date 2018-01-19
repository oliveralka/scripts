#!/usr/bin/env python3
import sys
import argparse
import os
import shutil
import requests
import zipfile
import xml.etree.ElementTree as ET
import csv
import re


def main(argv):

    na_string = 'NA'
    name_concentration_middle = 'concentration_middle'
    name_concentration_lower = 'concentration_lower'
    name_concentration_upper = 'concentration_upper'

    def handle_uncertainty(m):
        mean = float(m.group(1))
        sd = float(m.group(2))
        return (str(mean - sd), str(mean), str(mean + sd))

    def handle_regular(m):
        mean = float(m.group(1))
        return (mean, mean, mean)

    def handle_lower_bound(m):
        return (m.group(1), 'NA', 'NA')

    def handle_upper_bound(m):
        return ('NA', 'NA', m.group(1))

    def handle_upper_bound_exclusive_range(m):
        return (m.group(1), 'NA', m.group(2))

    re_handler = {
        'uncertainty':
        (re.compile(r'^([0-9]+(?:\.[0-9]+)?)\s*\+/-\s*([0-9]+(?:\.[0-9]+)?)$'),
         handle_uncertainty),
        'not_available':
        (re.compile(r'^NA$'),
         lambda x: (na_string, na_string, na_string)),
        'regular':
        (re.compile(r'^([0-9]+(?:\.[0-9]+)?)'),
         handle_regular),
        'lower_bound_exclusive':
        (re.compile(r'^>\s*([0-9]+(?:\.[0-9]+)?)$'),
         handle_lower_bound),  # >12.0
        'upper_bound_exclusive':
        (re.compile(r'^<\s*([0-9]+(?:\.[0-9]+)?)$'),
         handle_upper_bound),  # < 14
        'upper_bound_exclusive_range':
        (re.compile(r'^<\s*([0-9]+(?:\.[0-9]+)?)\s*(?:-|–)\s*([0-9]+(?:\.[0-9]+)?)$'),
         handle_upper_bound_exclusive_range),
        'upper_bound_inclusive':
        (re.compile(r'^<=\s*([0-9]+(?:\.[0-9]+)?)$'),
         handle_upper_bound),
        'upper_bound_exclusive_scientific':
        (re.compile(r'^<([0-9]+(?:\.[0-9]+)?e-?[0-9]+)$'),
         handle_upper_bound)   # <5.110e-05
    }

    parser = argparse.ArgumentParser()
    parser.add_argument('-o', type=str, required=True)
    parser.add_argument('--removetarget', action='store_true')
    args = parser.parse_args(argv[1:])

    if os.path.exists(args.o):
        if args.removetarget:
            shutil.rmtree(args.o)
        else:
            print("FATAL: Target already exists")
            sys.exit(1)
    os.mkdir(args.o)
    url = 'http://www.urinemetabolome.ca/system/downloads/current/urine_metabolites.zip'
    r = requests.get(url)
    result_file = os.path.join(args.o, 'urine_metabolites.zip')
    with open(result_file, 'wb') as f:
        f.write(r.content)
    with zipfile.ZipFile(result_file, "r") as zip_ref:
        zip_ref.extractall(args.o)
    os.remove(result_file)
    result_file = os.path.join(args.o, 'urine_metabolites.xml')
    concentration_file = os.path.join(args.o, 'urine_metabolites.csv')

    parser_it = ET.iterparse(result_file, events=['start', 'end'])

    attributes_metabolites = [
        'version',
        'creation_date',
        'update_date',
        'accession',
        'chemical_formula',
        'average_molecular_weight',
        'monisotopic_molecular_weight',
        'iupac_name',
        'traditional_iupac',
        'cas_registry_number',
        'smiles',
        'inchi',
        'inchikey'
    ]
    attributes_concentration = [
        'biofluid',
        'concentration_value',
        name_concentration_lower,
        name_concentration_middle,
        name_concentration_upper,
        'concentration_units',
        'subject_age',
        'subject_sex',
        'subject_condition'
    ]

    def get_value(value):
        if value is None:
            return 'NA'
        value = value.strip()
        if not value:
            return 'NA'
        return value

    def normalize(tag):
        tag = tag.replace(r'{http://www.hmdb.ca}', '')

        if tag == 'patient_age':
            return 'subject_age'
        if tag == 'patient_sex':
            return 'subject_sex'
        if tag == 'patient_condition':
            return 'subject_condition'
        return tag

    metabolite = {}
    normal_concentrations = []
    abnormal_concentrations = []

    concentration = {}
    concentration_abnormal = False

    with open(concentration_file, 'w') as outfile:
        outfile_csvwriter = csv.writer(outfile)
        outfile_csvwriter.writerow(
            attributes_metabolites + attributes_concentration +
            ['is_normal_concentration'])
        for (event, elem) in parser_it:
            tag = normalize(elem.tag)
            if event == 'start':
                if tag == 'normal_concentrations':
                    concentration_abnormal = False
                elif tag == 'abnormal_concentrations':
                    concentration_abnormal = True

            elif event == 'end':
                if tag == 'metabolite':

                    # Commit concentration with all metabolites and reset
                    row_metabolite = [metabolite[x] if x in metabolite else 'NA' for x in attributes_metabolites ]
                    for conc in normal_concentrations:
                        row_concentration = [ conc[x] if x in conc else 'NA' for x in attributes_concentration]
                        row_concentration.append(True)
                        outfile_csvwriter.writerow(row_metabolite + row_concentration)

                    for conc in abnormal_concentrations:
                        row_concentration = [conc[x] if x in conc else 'NA' for x in attributes_concentration]
                        row_concentration.append(False)
                        outfile_csvwriter.writerow(row_metabolite + row_concentration)

                    metabolite = {}
                    concentration = {}
                    normal_concentrations = []
                    abnormal_concentrations = []

                elif tag == 'concentration':

                    if 'concentration_value' in concentration:
                        concentration_value = concentration['concentration_value']
                        matched = False
                        for (name, (regex, handler)) in re_handler.items():
                            m = re.match(regex, concentration_value)
                            if m:
                                matched = True
                                (lower, mean, upper) = handler(m)
                                concentration[name_concentration_lower] = lower
                                concentration[name_concentration_middle] = mean
                                concentration[name_concentration_upper] = upper
                                break
                        if not matched:
                            raise ValueError('Concentration could not be parsed: ' + concentration_value)

                    if concentration_abnormal:
                        abnormal_concentrations.append(concentration)
                    else:
                        normal_concentrations.append(concentration)
                    concentration = {}
                else:
                    if tag in attributes_metabolites:
                        metabolite[tag] = get_value(elem.text)
                    elif tag in attributes_concentration:
                        concentration[tag] = get_value(elem.text)


if __name__ == '__main__':
    main(sys.argv)
