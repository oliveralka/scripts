#!/usr/bin/env python3
import sys
import argparse
import os
import shutil
import requests
import zipfile
import xml.etree.ElementTree as ET
import csv

def main(argv):
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
        outfile_csvwriter.writerow(attributes_metabolites + attributes_concentration + ['is_normal_concentration'])
        for (event, elem) in parser_it:
            tag = normalize(elem.tag)
            if event == 'start':
                if  tag == 'normal_concentrations':
                    concentration_abnormal = False
                elif tag == 'abnormal_concentrations':
                    concentration_abnormal = True

            elif event == 'end':
                if tag == 'metabolite':

                    # Commit concentration with all metabolites and reset
                    row_metabolite = [ metabolite[x] if x in metabolite else 'NA' for x in attributes_metabolites ]
                    for conc in normal_concentrations:
                        row_concentration = [ conc[x] if x in conc else 'NA' for x in attributes_concentration]
                        row_concentration.append(True)
                        outfile_csvwriter.writerow(row_metabolite + row_concentration)

                    for conc in abnormal_concentrations:
                        row_concentration = [ conc[x] if x in conc else 'NA' for x in attributes_concentration]
                        row_concentration.append(False)
                        outfile_csvwriter.writerow(row_metabolite + row_concentration)

                    metabolite = {}
                    concentration = {}
                    normal_concentrations = []
                    abnormal_concentrations = []

                elif tag == 'concentration':
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
