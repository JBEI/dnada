from typing import Optional

WORKFLOW_READMES = {
    0: """

# Synthetic Biology Workflow

**Follow the steps outlined in this directory for best results :)**

For the best viewing experience, open these README.md files in your
browser.
""",
    1: """

# Step 1 - Order Genes

The synths_plate.csv has a column named *'Sequence'* that
contains the sequence for all the genes you need to order.
Place your orders through your favorite gene synthesis vendor.
""",
    2: """

# Step 2 - Order Oligos

This directory contains a csv file named *'oligos_order_96.csv'* to use in
ordering the oligos.

## How to order a 96 well plate of oligos through IDT:
1. Open the csv file in your favorite spreadsheet application.
2. Delete the unnamed column containing indexes (column A).
3. Save the file in as an .xls or .xlsx file.
4. Submit the file to IDT for 96-well plate ordering.
5. Order oligos.

## How to order oligos as tubes through IDT:
1. Open the same csv file in your favorite spreadsheet application.
2. Copy the *'Name'* and *'Sequence'* columns into a new spreadsheet.
3. Add columns with names *'Scale'* and *'Purification'*.
4. For all oligos, enter *'25nm'* in the *'Scale'* column, and *'STD'* in
the *'Purification'* column.
* This is the minumum amount of oligos you can buy when oligos are 15-60
bp.
* For oligos larger than 60 bp, you may need to increase the scale and
change the purification method
5. Aliquot oligos at 50 mM into wells in an Echo PP plate as defined by
the *'templates_plate.csv'* file.
* This will be 50 uL of each oligo per well
* Follow the *'PLATE WELL'* column for well locations per each oligo
""",
    3: """

# Step 3 - Order and prepare templates

Order the templates from the registry.

## How to order templates from the registry:
1. Open the *'templates_plate.csv'* file in your favorite spreadsheet
application.
2. Note each value in the *'LIQUID TYPE'* column that starts with *'p'*.
* The *'LIQUID TYPE'* column values that start with *'dsDVA'* are
synthetic parts you purchase from a vendor.
3. For each of those values, search for them in the correct registry
instance:
* [JPUB ICE](https://public-registry.jbei.org)
4. Find the associated strain for the part, and go to the strain.
5. Click on *'Samples'* in the *'General Information'* box.
6. Select a sample, add to cart, and enter information on how you want
the strain.
The strain/template is now ordered.

## How to prepare templates for PCR:
1. Fill an Echo PP plate with templates at 50 uL per well as defined by
the *'templates_plate.csv'* file.
* If using liquid culture, aliquot the culture at 1X into well.
* If using synthesized DNA, aliquot at 10 ng/uL into well.
* If using purified plasmid, aliquot at 10 ng/uL into well.
""",
    4: """

# Step 4 - Perform PCRs

## How to transfer reagents with Echo:
1. Bring your Build Automation files, templates plate, oligos plate, and
a skirted 96 well plate to the Echo.
2. Open the *'Echo Liquid Handler Software'* on the machine.
3. Go to the *'Calibration'* tab, and click on the *'Focus'* button within
the *'Transducer'* box.
4. Wait for the Echo to calibrate, do not insert any plates.
5. View the calibration results, there should be a -x<sup>2</sup> shape if
the calibration is sufficient.
6. Open the *'Echo Plate Reformat'* software.
7. Start a new method.
8. Select *'384PP'* plates for source, '*384PP_AQ_BP2'* for Default Plate
Type, *'Biorad 96 Hardshell PCR'* for destination, and *'Custom'* for
mapping.
9. Click the button in the toolbar that looks like a spreadsheet.
10. Import your *'pcr_echo_instructions.csv'* file.
11. Follow the Echo instructions to perform the transfer.

## How to prepare the PCR:
1. Bring your Build Automation files, oligos/templates plate, no-skirt 96
well plate, nuclease-free water,
and PCR master mix to the Biomek FXP.
2. Open the Biomek Software.
3. Open the project *'NGS'* (note this may change in the future).
4. Open the method *'NGS_1. PCR setup'* (this naming might change).
5. Click both *'Start'* and *'Finish'* in the Biomek Software, and confirm
that there are no errors.
* If there are errors, troubleshoot yourself or ask an Automation Engineer
for assistance.
6. Click *'Run'*, and when prompted to submit a file, submit your file
from Build Automation: *'pcr_biomek_instructions.csv'*.
7. Always choose to prime the syringes, and let the syringes prime until
you do not see any bubbles.
8. When prompted, select the first row of tips to use (should be 1 if you
use a new box of tips).
9. The software should then open another application and show a deck
layout.
10. Now, load the deck including your samples and master mix.
11. Click *'Finish'*, and the method will run. Stay by the robot
throughout the method in case any errors occur.
12. When complete, the software will ask if you want to return to 25C.
Say *'Yes'*.
13. Now go behing the Biomek FXP and touch the *'Temp.'* button on the
cooler to turn it off (needs to be unfilled).
14. Take your no skirt plate of PCR reactions and move to the Veriti
thermocyclers.

## How to run the PCR:
1. Bring your plate of reactions, and your *'clean_pcr_worksheet.csv'*
printed.
2. Set up the Veriti thermocycler according to the zones defined in the
 *'clean_pcr_worksheet.csv'* and your polymerase parameters.
* Veriti can create *'zones'* that are two columns wide. These zones
can be different temperatures.
* Your PCR plate should be organized by zones from left to right, and
zones can be programmed accordingly.
* Read your worksheet's columns *'OUTPUT_WELL'* and
*'THERMOCYCLER_ZONE_ANNEALING_TEMP'* for zone programming.
* Program your denaturing and extension temperares and times according to
 your polymerase specifications.
""",
    5: """

# Step 5 - Analyze PCRs

This is a quick protocol for running ZAG. For the full ZAG protocol, visit
this.

## How to prepare PCRs for ZAG
1. Retrieve a clean no-skirt or semi-skirt 96 well plate.
2. Fill every well in the plate with 23.5 uL of ZAG dilution buffer.
* This can be done with a multichannel pipette.
* All wells must be filled, even wells that will not contain samples.
3. Aliquot 0.75 uL of ZAG 1kb ladder to well H12.
* Do not include any sample in this well.
4. Add one drop of mineral oil on top of the H12 well with the ladder.
5. Aliquot 0.5 uL of your sample into wells of the plate.
* Keep the same plate format as your PCR plate.
6. Seal your plate with a Biorad *'B'* or *'F'* seal.
7. Vortex the plate, and then centrifuge at 3000-4000 rcf for 30 seconds.

## How to run PCRs on ZAG
1. Open the ZAG application on the ZAG computer.
2. Open the waste tray in the *'W'* slot, empty it in the sink, rinse it
out, and put it back in the ZAG.
3. Take the seal off of your plate, and put it in any empty slot that is
not *'B'* or *'W'*.
* Make sure the A1 well is at the stop left in the slot.
4. In the ZAG application, click the box for your slot. Then click
*'Add to queue'*.
5. Change the method to *'ZAG130 gel prime only'*.
6. Change the file path to a naming convention containing the date and
your experiment name.
* Ex: 200618_zagagilent_testproject_1
7. Click the green arrow in the ZAG application to start the run.
8. Wait 45-50 minutes for the run to complete.

## How to export and analyze ZAG PCR data
1. Open the ZAG application on the ZAG computer.
2. Open the *'.raw'* file from your run in your named directory.
3. Click the *'export'* button to export the data.
* Export all your samples with alternate peak table.
* Image format should be png.
* Export a pdf of the data by clicking *'pdf report'* if desired.
4. Go to the [Build Automation](https://cloudenzymes.com/) application.
5. Click the *'Analyze ZAG Data'* button, import your peak tables csv
and size worksheet.
* Fill all other data related to your samples as well.
6. click *'Submit'*, and downlaod your results.

The results should explain which PCRs were successful, and which
reactions need a redo.
""",
    6: """

# (optional) Step 6 - Redo Failed PCRs
""",
    7: """

# (if necessary) Step 7 - Consolidate PCRs
""",
    8: """

# Step 8 - Restriction Digests

## DpnI from NEB
1. Prepare a master mix such that each component is multiplied by X number
of sample wells + 0.5:
* 1 uL CutSmart Buffer
* 18.5 uL ultrapure water
* 0.25 uL DpnI
Prepare these into a tapered screw top 1.5 mL tube.
[Example tube](https://ecatalog.corning.com/life-sciences/b2c/US/en/
General-Labware/Tubes/Microcentrifuge-Tubes/Corning%C2%AE-Screw-Cap-
Polypropylene-Microcentrifuge-Tubes/p/430909)

For example, a master mix for three reactions would be:
* 1 uL Cutsmart * (3 + 0.5) = 3.5 uL CutSmart
* 0.25 uL DpnI * (3 + 0.5) = 0.88 uL DpnI
* 18.75 uL ulrapure water * (3 + 0.5) = 65.7 uL ultrapure water

2. Vortex the master mix, and keep on ice until use.

## Automated addition of master mix with Biomek FXp
1. Bring your Build Automation files, PCR plate, and enzyme
master mix to the Biomek FXP.
2. Open the Biomek Software.
3. Open the project *'NGS'* (note this may change in the future).
4. Open the method *'tube-to-plate_v2'* (this naming might
change).
5. Click both *'Start'* and *'Finish'* in the Biomek Software,
and confirm that there are no errors.
* If there are errors, troubleshoot yourself or ask an Automation
 Engineer for assistance.
6. Click *'Run'*, and when prompted to submit a file, submit your
 file from Build Automation: *'dpni_biomek_instructions.csv'*.
7. Always choose to prime the syringes, and let the syringes prime
 until you do not see any bubbles.
8. Enter a volume to transfer from the master mix to each well.
* This should be 20 (uL) if using the DpnI formula given above
9. The software will prompt and ask to select '96 rack' or '96.
Choose the option reflecting your sample plate.
The '96 rack' is for no skirt plates in a 96 well plate rack. The
 '96' option is for skirt/semi-skirt plates.
* Most of the time, this will be the '96 rack' option if running
 the method on a PCR plate used in the Veriti thermocycler.
10. Load deck when instructed, which should be when the Biomek
Method Launcher starts.
* Be sure to unseal your plate and remove the lid on the enzyme
master mix tube.
11. In Biomek Method Launcher, click 'finish' when deck is set
up to run the method.

## Running the digestion reaction
1. Seal your plate after adding the enzyme master mix.
2. Vortex and centrifuge your plate to mix and make it ready for
digestion.
3. Put the plate in a Veriti thermocycler, and run a program
consisting of the following:
* 37°C for 1 hour
* 80°C for 15 minutes
* 10°C forever
4. Retrieve the plate once at the last step (10°C hold).
""",
    9: """

# Step 9 - PCR Cleanup

## How to purify PCR amplicons with Ampure beads
1. Bring the following to the Biomek FXP:
* *'BeadMethod_template.csv'*
* 50 mL of 80 percent ethanol
* Nuclease-free water
* AMPure XP beads
* Skirt 96 well plate
* No-skirt 96 well plate
* PCR plate
2. Open the Biomek Software.
3. Open the NGS project.
4. Open the method *'Bead_XXXXXXXX_name'*.
5. Click both *'Start'* and *'Finish'* in the Biomek Software,
and confirm that there are no errors.
* If there are errors, troubleshoot yourself or ask an Automation
 Engineer for assistance.
6. Click *'Run'*, and when prompted ot submit a file, submit your
 file from Build Automation: *'BeadMethod_template.csv'*.
7. Always choose to prime the syringes, and let the syringes prime
 until you do not see any bubbles.
8. Load the deck as defined by the software.
* This includes tall, low, and 40 mL reservoirs
    * The 40 mL reservoirs can be found under the Caliper instrument
     next to the ZAG
* Beads are to be aliquoted in the 40 mL reservoirs, and mounted
in a hollow, transparent rack on the deck
* Bead volume to aliquot is the total of beads defined in the
*'BeadMethod_tempalte.csv'* file, + 2-3 uL
* The magnet is in a drawer labeled *'Biomek Tools'* under the
 Veriti thermocyclers
* Do not load the ethanol before satrting, the method prompts
 the user to add the ethanol later
9. Run the method.
* This takes about an hour to run.
10. Retrieve your purified DNA plate and remove all other components
 from the deck.
""",
    10: """

# (optional) Step 10 - Quantify DNA Part Yield

## How to prepare a quantification plate with Echo:
1. Bring the following to the Echo:
* *'quant_echo_instructions.csv'*
* Dark 96 well plate
* Purified PCR plate
* Digestions plate (if part of design)
2. Open the *'Echo Liquid Handler Software'* on the
machine.
3. Go to the *'Calibration'* tab, and click on the
*'Focus'* button within the *'Transducer'* box.
4. Wait for the Echo to calibrate, do not insert any plates.
5. View the calibration results, there should be a
-x<sup>2</sup> shape if the calibration is sufficient.
6. Open the *'Echo Plate Reformat'* software.
7. Start a new method.
8. Select *'384PP'* plates for source, '*Flat 96 C'*
for Default Plate Type,
*'Biorad 96 Hardshell PCR'* for destination, and *'Custom'* for mapping.
9. Click the button in the toolbar that looks like a spreadsheet.
10. Import your *'quant_echo_instructions.csv'* file.
11. Follow the Echo instructions to perform the transfer.
12. After performing the Echo transfer, add 2 uL of each
standard to the last column of the plate.
* This can be done with a multichannel pipette.

## How to quantify DNA part yields:
1. Follow Quantiflour instructions to prepare the buffer/reagent mixture.
2. Aliquot 50 uL of buffer to each sample well with a multichannel pipette.
3. Prepare one well as a blank with no DNA, but with buffer.
4. Go to the Biomek NX-S8 with your plate.
5. Open the protocol *'DNA_Quant_Calibration_Column_12'*.
6. Insert the plate into the plate reader, and run.
7. Save your results, and analyze the data to prepare
 concentrations for your DNA.
8. Save DNA concentration in the *'quant_worksheet.csv'*.
""",
    11: """

# Step 11 - Perform Assembly

This can be done with equimolar or equivolume amounts for each part.

For equivolume, be sure to use the *'assembly_echo_instructions.csv'* file.

For equimolar, be sure to use the
*'assembly_echo_instructions_equimolar.csv'* or
*'assembly_water_echo_instructions_equimolar.csv'* file.
* These can be prepared with the *'Create Equimolar Instructions'*
and *'Create Equimolar and Water Transfer Instructions'*
standalone methods.

## How to prepare an assembly plate with Echo
* Note that for equivolume, *'file'* will be the
*'assembly_echo_instructions.csv'* file.
* Note that for equimolar, *'file'* will be the
*'assembly_echo_instructions_equimolar.csv'* file
    * *'file_water'* will be the
    *'assembly_water_echo_instructions_equimolar.csv'* file
1. Bring the following to the Echo:
* All parts plates
* A 384PP plate
* Your *'file'* or *'file_water'* if obtained
    * If using the *'file_water'*, prepare a 384PP plate with 65 uL of
    water in each well used in the *'file_water'* for the
    'water_plate_1'*.
2. Open the *'Echo Liquid Handler Software'* on the machine.
3. Go to the *'Calibration'* tab, and click on the *'Focus'*
button within the *'Transducer'* box.
4. Wait for the Echo to calibrate, do not insert any plates.
5. View the calibration results, there should be a
-x<sup>2</sup> shape if the calibration is sufficient.
6. Open the *'Echo Plate Reformat'* software.
7. Start a new method.
8. Select *'384PP'* plates for source, '*384PP_AQ_BP2'* for Default
Plate Type,
*'384PP'* for destination, and *'Custom'* for mapping.
9. Click the button in the toolbar that looks like a spreadsheet.
10. Import your *'file'* or *'file_water'* if obtained.
11. Follow the Echo instructions to perform the transfer.

## How to add water to the assembly plate
1. Aliquot an amount of water to each assembly well such
that:
```
water_to_aliquot = desired_assembly_volume -
desired_assembly_volume/master_mix_concentration -
parts_volume
```
* Note that if you used the *'file_water'* in the Echo, the water
aliquot was already performed, so this step is not necessary.

##Automated addition of assembly master mix with Biomek FXp
1. Bring your Build Automation files, PCR plate, and thawed 2X assembly
 master mix to the Biomek FXP.
2. Open the Biomek Software.
3. Open the project *'NGS'* (note this may change in the future).
4. Open the method *'tube-to-plate_v2'* (this naming might change).
5. Click both *'Start'* and *'Finish'* in the Biomek Software, and confirm
 that there are no errors.
* If there are errors, troubleshoot yourself or ask an Automation Engineer
 for assistance.
6. Click *'Run'*, and when prompted to submit a file, submit your file
from Build Automation: *'assembly_biomek_instructions.csv'*.
7. Always choose to prime the syringes, and let the syringes prime until
you do not see any bubbles.
8. Enter a volume to transfer from the master mix to each well.
* This should be 10 (uL) if performing a 20 uL assembly with 10 uL of
parts/water
9. The software will prompt and ask to select '96 rack' or '96. Choose the
 option reflecting your sample plate.
The '96 rack' is for no skirt plates in a 96 well plate rack. The '96'
option is for skirt/semi-skirt plates.
* Most of the time, this will be the '96' option if running the method
on a hardshell plate used in the Tetrad thermocycler.
10. Load deck when instructed, which should be when the Biomek Method
Launcher starts.
* Be sure to unseal your plate and remove the lid on the enzyme master
mix tube.
11. In Biomek Method Launcher, click 'finish' when deck is set up to run
the method.

## How to perform an assembly
1. Program a Veriti or Tetrad to perform an assembly reaction as defined
by your master mix manufacturer's protocol.
2. Insert your plate into the Veriti or Tetrad and run the program.
""",
    12: """

# (if yeast assembly) Step 12 - Yeast Plasmid Prep
""",
    13: """

# Step 13 - E. coli Transformation

Manual for the time being. Automated method currently in development.
""",
    14: """

# Step 14 - Colony Picking
""",
    15: """

# Step 15 - Request Sequencing Services

Prepare and submit a sample submission form for NGS services
""",
    16: """

# Step 16 - Prepare and submit NGS samples

Prepare samples by boiling 20 uL of each overnight culture for 
10 minutes in 20 uL of water.
""",
    17: """

# Step 17 - Analyze NGS results

Follow the insructions given by your NGS service provider 
to analyze your data. The results should be a csv containing
construct IDs and whether or not they were successful.
""",
    18: """

# Step 18 - Cherry-pick successful constructs
""",
    19: """

# Step 19 - Submit to registry
""",
}


def workflow_readme(step: int) -> Optional[str]:
    assert step in WORKFLOW_READMES.keys()
    return WORKFLOW_READMES.get(step)
