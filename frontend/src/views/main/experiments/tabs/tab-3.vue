<template>
  <div>
    <v-card class="ma-3 pa-3">
      <v-card-title primary-title>
        <div class="headline primary--text">Workflow</div>
      </v-card-title>
      <v-card-text>
        <div v-if="JSON.stringify(activeWorkflow) === '{}'">
          Please activate an automation result to view a workflow
        </div>
        <div v-else>
          <v-subheader
            >Viewing workflow for automation result from
            {{ activeWorkflow.created_time }}</v-subheader
          >
          <v-stepper v-model="workflowStep" vertical non-linear>
            <v-stepper-step editable :complete="workflowStatus.step1" step="1"
              >Order genes to synthesize</v-stepper-step
            >
            <v-stepper-content step="1">
              <v-card>
                <v-card-text>
                  <v-list subheader nav dense flat disabled>
                    <v-subheader>Instructions</v-subheader>
                    <v-list-item-group>
                      <v-list-item>
                        <v-list-item-content
                          >• Order genes from vendor</v-list-item-content
                        >
                      </v-list-item>
                      <v-list-item>
                        <v-list-item-content
                          >• Add genes to templates echo
                          plate</v-list-item-content
                        >
                      </v-list-item>
                    </v-list-item-group>
                  </v-list>
                </v-card-text>
                <v-card-actions>
                  <v-switch
                    v-model="workflowStatus.step1"
                    label="Mark Complete"
                  ></v-switch>
                </v-card-actions>
              </v-card>
            </v-stepper-content>
            <v-stepper-step editable :complete="workflowStatus.step2" step="2"
              >Order oligos to synthesize</v-stepper-step
            >
            <v-stepper-content step="2">
              <v-card>
                <v-card-text>
                  <v-list subheader nav dense flat disabled>
                    <v-subheader>Instructions</v-subheader>
                    <v-list-item-group>
                      <v-list-item>
                        <v-list-item-content
                          >• Download oligo order worksheet</v-list-item-content
                        >
                      </v-list-item>
                      <v-list-item>
                        <v-list-item-content
                          >• Order oligos from IDT (or other
                          vendor)</v-list-item-content
                        >
                      </v-list-item>
                      <v-list-item>
                        <v-list-item-content
                          >• Move oligos to oligos echo
                          plate</v-list-item-content
                        >
                      </v-list-item>
                    </v-list-item-group>
                  </v-list>
                </v-card-text>
                <v-card-actions>
                  <v-switch
                    v-model="workflowStatus.step2"
                    label="Mark Complete"
                  ></v-switch>
                </v-card-actions>
              </v-card>
            </v-stepper-content>
            <v-stepper-step editable :complete="workflowStatus.step3" step="3"
              >Order templates from registry</v-stepper-step
            >
            <v-stepper-content step="3">
              <v-card>
                <v-card-text>
                  <v-list subheader nav dense flat disabled>
                    <v-subheader>Instructions</v-subheader>
                    <v-list-item-group>
                      <v-list-item>
                        <v-list-item-content
                          >• Download template worksheet</v-list-item-content
                        >
                      </v-list-item>
                      <v-list-item>
                        <v-list-item-content
                          >• Order templates from registry</v-list-item-content
                        >
                      </v-list-item>
                      <v-list-item>
                        <v-list-item-content
                          >• Miniprep templates or extract
                          gDNA</v-list-item-content
                        >
                      </v-list-item>
                      <v-list-item>
                        <v-list-item-content
                          >• Add purified templates to templates echo
                          plate</v-list-item-content
                        >
                      </v-list-item>
                    </v-list-item-group>
                  </v-list>
                </v-card-text>
                <v-card-actions>
                  <v-switch
                    v-model="workflowStatus.step3"
                    label="Mark Complete"
                  ></v-switch>
                </v-card-actions>
              </v-card>
            </v-stepper-content>
            <v-stepper-step editable :complete="workflowStatus.step4" step="4"
              >Perform PCRs</v-stepper-step
            >
            <v-stepper-content step="4">
              <v-card>
                <v-card-text>
                  <v-list subheader nav dense flat disabled>
                    <v-subheader>Instructions</v-subheader>
                    <v-list-item-group>
                      <v-list-item>
                        <v-list-item-content
                          >• Download PCR worksheet</v-list-item-content
                        >
                      </v-list-item>
                      <v-list-item>
                        <v-list-item-content
                          >• Use echo instructions to distribute oligos and
                          templates</v-list-item-content
                        >
                      </v-list-item>
                      <v-list-item>
                        <v-list-item-content
                          >• Use biomek instructions to distribute water and PCR
                          master mix</v-list-item-content
                        >
                      </v-list-item>
                      <v-list-item>
                        <v-list-item-content
                          >• Use thermocycler instructions to set up
                          thermocycler</v-list-item-content
                        >
                      </v-list-item>
                    </v-list-item-group>
                  </v-list>
                </v-card-text>
                <v-card-actions>
                  <v-switch
                    v-model="workflowStatus.step4"
                    label="Mark Complete"
                  ></v-switch>
                </v-card-actions>
              </v-card>
            </v-stepper-content>
            <v-stepper-step editable :complete="workflowStatus.step5" step="5"
              >Analyze PCRs</v-stepper-step
            >
            <v-stepper-content step="5">
              <v-card>
                <v-card-text>
                  <v-list nav dense flat disabled>
                    <v-subheader>Instructions</v-subheader>
                    <v-list-item-group>
                      <v-list-item>
                        <v-list-item-content
                          >• Prepare PCR samples for ZAG by aliquoting in sample
                          buffer</v-list-item-content
                        >
                      </v-list-item>
                      <v-list-item>
                        <v-list-item-content>• Run ZAG</v-list-item-content>
                      </v-list-item>
                      <v-list-item>
                        <v-list-item-content
                          >• Upload ZAG results here</v-list-item-content
                        >
                      </v-list-item>
                      <v-list-item>
                        <v-list-item-content
                          >• View results and decide whether to redo failed
                          PCRs</v-list-item-content
                        >
                      </v-list-item>
                    </v-list-item-group>
                  </v-list>
                </v-card-text>
                <v-card-actions>
                  <v-btn @click="analyzePCRDialog = true">
                    Analyze
                    <v-icon>mdi-dna</v-icon>
                  </v-btn>
                  <v-spacer></v-spacer>
                  <v-switch
                    v-model="workflowStatus.step5"
                    label="Mark Complete"
                  ></v-switch>
                </v-card-actions>
              </v-card>
            </v-stepper-content>
            <v-stepper-step editable :complete="workflowStatus.step6" step="6"
              >(optional) Redo Failed PCRs</v-stepper-step
            >
            <v-stepper-content step="6">
              <v-card>
                <v-card-text>
                  <v-list nav dense flat disabled>
                    <v-subheader>Instructions</v-subheader>
                    <v-list-item-group>
                      <v-list-item>
                        <v-list-item-content
                          >• Download Redo PCR worksheet</v-list-item-content
                        >
                      </v-list-item>
                      <v-list-item>
                        <v-list-item-content
                          >• Use echo instructions to distribute oligos and
                          templates</v-list-item-content
                        >
                      </v-list-item>
                      <v-list-item>
                        <v-list-item-content
                          >• Use biomek instructions to distribute water and PCR
                          master mix</v-list-item-content
                        >
                      </v-list-item>
                      <v-list-item>
                        <v-list-item-content
                          >• Use thermocycler instructions to set up
                          thermocycler</v-list-item-content
                        >
                      </v-list-item>
                      <v-list-item>
                        <v-list-item-content
                          >• Prepare PCR samples for ZAG by aliquoting in sample
                          buffer</v-list-item-content
                        >
                      </v-list-item>
                      <v-list-item>
                        <v-list-item-content>• Run ZAG</v-list-item-content>
                      </v-list-item>
                      <v-list-item>
                        <v-list-item-content
                          >• Upload ZAG results here</v-list-item-content
                        >
                      </v-list-item>
                      <v-list-item>
                        <v-list-item-content
                          >• View results and decide whether to redo failed
                          PCRs</v-list-item-content
                        >
                      </v-list-item>
                      <v-list-item>
                        <v-list-item-content
                          >• Repeat this step as necessary</v-list-item-content
                        >
                      </v-list-item>
                    </v-list-item-group>
                  </v-list>
                </v-card-text>
                <v-card-actions>
                  <v-btn>
                    Download
                    <v-icon>mdi-download</v-icon>
                  </v-btn>
                </v-card-actions>
              </v-card>
            </v-stepper-content>
            <v-stepper-step editable :complete="workflowStatus.step7" step="7"
              >(if necessary) Consolidate PCRs</v-stepper-step
            >
            <v-stepper-content step="7">
              <v-card>
                <v-card-text>
                  <v-list nav dense flat disabled>
                    <v-subheader>Instructions</v-subheader>
                    <v-list-item-group>
                      <v-list-item>
                        <v-list-item-content
                          >• Download Consolidate PCR
                          worksheet</v-list-item-content
                        >
                      </v-list-item>
                      <v-list-item>
                        <v-list-item-content
                          >• Use biomek instructions to consolidate
                          PCRs</v-list-item-content
                        >
                      </v-list-item>
                    </v-list-item-group>
                  </v-list>
                </v-card-text>
                <v-card-actions>
                  <v-btn>
                    Download
                    <v-icon>mdi-download</v-icon>
                  </v-btn>
                </v-card-actions>
              </v-card>
            </v-stepper-content>
            <v-stepper-step editable :complete="workflowStatus.step8" step="8"
              >DpnI Digestion</v-stepper-step
            >
            <v-stepper-content step="8">
              <v-card>
                <v-card-text>
                  <v-list nav dense flat disabled>
                    <v-subheader>Instructions</v-subheader>
                    <v-list-item-group>
                      <v-list-item>
                        <v-list-item-content
                          >• Download Digestion worksheet</v-list-item-content
                        >
                      </v-list-item>
                      <v-list-item>
                        <v-list-item-content
                          >• Use biomek instructions to distribute dpnI and FD
                          buffer</v-list-item-content
                        >
                      </v-list-item>
                      <v-list-item>
                        <v-list-item-content
                          >• Thermocycle at 37C for up to 90
                          minutes</v-list-item-content
                        >
                      </v-list-item>
                    </v-list-item-group>
                  </v-list>
                </v-card-text>
                <v-card-actions>
                  <v-btn>
                    Download
                    <v-icon>mdi-download</v-icon>
                  </v-btn>
                </v-card-actions>
              </v-card>
            </v-stepper-content>
            <v-stepper-step editable :complete="workflowStatus.step9" step="9"
              >PCR Cleanup</v-stepper-step
            >
            <v-stepper-content step="9">
              <v-card>
                <v-card-text>
                  <v-list nav dense flat disabled>
                    <v-subheader>Instructions</v-subheader>
                    <v-list-item-group>
                      <v-list-item>
                        <v-list-item-content
                          >• Download PCR Cleanup worksheet</v-list-item-content
                        >
                      </v-list-item>
                      <v-list-item>
                        <v-list-item-content
                          >• Use biomek instructions to perform PCR cleanup with
                          magbeads</v-list-item-content
                        >
                      </v-list-item>
                      <v-list-item>
                        <v-list-item-content
                          >• After cleaning up, stamp PCR plate(s) into echo
                          plate(s)</v-list-item-content
                        >
                      </v-list-item>
                    </v-list-item-group>
                  </v-list>
                </v-card-text>
                <v-card-actions>
                  <v-btn>
                    Download
                    <v-icon>mdi-download</v-icon>
                  </v-btn>
                </v-card-actions>
              </v-card>
            </v-stepper-content>
            <v-stepper-step editable :complete="workflowStatus.step10" step="10"
              >(optional) Quantify Part Yield</v-stepper-step
            >
            <v-stepper-content step="10">
              <v-card>
                <v-card-text>
                  <v-list nav dense flat disabled>
                    <v-subheader>Instructions</v-subheader>
                    <v-list-item-group>
                      <v-list-item>
                        <v-list-item-content
                          >• Download Part Quantification
                          worksheet</v-list-item-content
                        >
                      </v-list-item>
                      <v-list-item>
                        <v-list-item-content
                          >• Use echo instructions to distribute
                          parts</v-list-item-content
                        >
                      </v-list-item>
                      <v-list-item>
                        <v-list-item-content
                          >• Use biomek instructions to distribute sample
                          buffer</v-list-item-content
                        >
                      </v-list-item>
                      <v-list-item>
                        <v-list-item-content
                          >• Upload results here</v-list-item-content
                        >
                      </v-list-item>
                    </v-list-item-group>
                  </v-list>
                </v-card-text>
                <v-card-actions>
                  <v-btn>
                    Download
                    <v-icon>mdi-download</v-icon>
                  </v-btn>
                </v-card-actions>
              </v-card>
            </v-stepper-content>
            <v-stepper-step editable :complete="workflowStatus.step11" step="11"
              >Perform assembly</v-stepper-step
            >
            <v-stepper-content step="11">
              <v-card>
                <v-card-text>
                  <v-list nav dense flat disabled>
                    <v-subheader>Instructions</v-subheader>
                    <v-list-item-group>
                      <v-list-item>
                        <v-list-item-content
                          >• Decide equimolar vs equivolume
                          assembly</v-list-item-content
                        >
                      </v-list-item>
                      <v-list-item>
                        <v-list-item-content
                          >• Download assembly worksheet</v-list-item-content
                        >
                      </v-list-item>
                      <v-list-item>
                        <v-list-item-content
                          >• Use echo instructions to distribute
                          parts</v-list-item-content
                        >
                      </v-list-item>
                      <v-list-item>
                        <v-list-item-content
                          >• If gibson/golden-gate use biomek instructions to
                          distribute assembly master mix. If yeast assembly,
                          perform manually.</v-list-item-content
                        >
                      </v-list-item>
                      <v-list-item>
                        <v-list-item-content
                          >• Perform assembly incubation, e.g. 3 day at 30C for
                          yeast, 1 hour at room T for
                          gibson</v-list-item-content
                        >
                      </v-list-item>
                    </v-list-item-group>
                  </v-list>
                </v-card-text>
                <v-card-actions>
                  <v-btn>
                    Download
                    <v-icon>mdi-download</v-icon>
                  </v-btn>
                </v-card-actions>
              </v-card>
            </v-stepper-content>
            <v-stepper-step editable :complete="workflowStatus.step12" step="12"
              >(if yeast assembly) Yeast Plasmid Prep</v-stepper-step
            >
            <v-stepper-content step="12">
              <v-card>
                <v-card-text>
                  <v-list nav dense flat disabled>
                    <v-subheader>Instructions</v-subheader>
                    <v-list-item-group>
                      <v-list-item>
                        <v-list-item-content
                          >• Plasmid prep the yeast</v-list-item-content
                        >
                      </v-list-item>
                    </v-list-item-group>
                  </v-list>
                </v-card-text>
                <v-card-actions>
                  <v-btn>
                    Download
                    <v-icon>mdi-download</v-icon>
                  </v-btn>
                </v-card-actions>
              </v-card>
            </v-stepper-content>
            <v-stepper-step editable :complete="workflowStatus.step13" step="13"
              >E. coli Transformation</v-stepper-step
            >
            <v-stepper-content step="13">
              <v-card>
                <v-card-text>
                  <v-list nav dense flat disabled>
                    <v-subheader>Instructions</v-subheader>
                    <v-list-item-group>
                      <v-list-item>
                        <v-list-item-content
                          >• Download transformation
                          worksheet</v-list-item-content
                        >
                      </v-list-item>
                      <v-list-item>
                        <v-list-item-content
                          >• Use biomek instructions to transform E.
                          coli</v-list-item-content
                        >
                      </v-list-item>
                      <v-list-item>
                        <v-list-item-content
                          >• Use Qpix or manually plate E. coli onto 48-well
                          q-plates</v-list-item-content
                        >
                      </v-list-item>
                      <v-list-item>
                        <v-list-item-content
                          >• Incubate overnight at 37C</v-list-item-content
                        >
                      </v-list-item>
                    </v-list-item-group>
                  </v-list>
                </v-card-text>
                <v-card-actions>
                  <v-btn>
                    Download
                    <v-icon>mdi-download</v-icon>
                  </v-btn>
                </v-card-actions>
              </v-card>
            </v-stepper-content>
            <v-stepper-step editable :complete="workflowStatus.step14" step="14"
              >Colony Picking</v-stepper-step
            >
            <v-stepper-content step="14">
              <v-card>
                <v-card-text>
                  <v-list nav dense flat disabled>
                    <v-subheader>Instructions</v-subheader>
                    <v-list-item-group>
                      <v-list-item>
                        <v-list-item-content
                          >• Upload images of plates here</v-list-item-content
                        >
                      </v-list-item>
                      <v-list-item>
                        <v-list-item-content
                          >• Use Qpix to pick E. coli
                          colonies</v-list-item-content
                        >
                      </v-list-item>
                      <v-list-item>
                        <v-list-item-content
                          >• Incubate at 37C overnight</v-list-item-content
                        >
                      </v-list-item>
                      <v-list-item>
                        <v-list-item-content
                          >• Upload Qpix picking worksheet
                          here</v-list-item-content
                        >
                      </v-list-item>
                    </v-list-item-group>
                  </v-list>
                </v-card-text>
                <v-card-actions>
                  <v-btn>
                    Download
                    <v-icon>mdi-download</v-icon>
                  </v-btn>
                </v-card-actions>
              </v-card>
            </v-stepper-content>
            <v-stepper-step editable :complete="workflowStatus.step15" step="15"
              >Submit for NGS</v-stepper-step
            >
            <v-stepper-content step="15">
              <v-card>
                <v-card-text>
                  <v-list nav dense flat disabled>
                    <v-subheader>Instructions</v-subheader>
                    <v-list-item-group>
                      <v-list-item>
                        <v-list-item-content
                          >• Download NGS worksheet</v-list-item-content
                        >
                      </v-list-item>
                      <v-list-item>
                        <v-list-item-content
                          >• Submit NGS worksheet
                        </v-list-item-content>
                      </v-list-item>
                    </v-list-item-group>
                  </v-list>
                </v-card-text>
                <v-card-actions>
                  <v-btn>
                    Download
                    <v-icon>mdi-download</v-icon>
                  </v-btn>
                </v-card-actions>
              </v-card>
            </v-stepper-content>
            <v-stepper-step editable :complete="workflowStatus.step16" step="16"
              >Prepare and submit NGS samples</v-stepper-step
            >
            <v-stepper-content step="16">
              <v-card>
                <v-card-text>
                  <v-list nav dense flat disabled>
                    <v-subheader>Instructions</v-subheader>
                    <v-list-item-group>
                      <v-list-item>
                        <v-list-item-content
                          >• Prepare glycerol stocks and boil preps of overnight
                          cultures</v-list-item-content
                        >
                      </v-list-item>
                      <v-list-item>
                        <v-list-item-content
                          >• Freeze glycerol stocks at -80C</v-list-item-content
                        >
                      </v-list-item>
                      <v-list-item>
                        <v-list-item-content
                          >• Stamp boil preps into echo plate and submit to
                          archival freezer</v-list-item-content
                        >
                      </v-list-item>
                      <v-list-item>
                        <v-list-item-content
                          >• Wait 10 days for results</v-list-item-content
                        >
                      </v-list-item>
                    </v-list-item-group>
                  </v-list>
                </v-card-text>
              </v-card>
            </v-stepper-content>
            <v-stepper-step editable :complete="workflowStatus.step17" step="17"
              >Analyze NGS results</v-stepper-step
            >
            <v-stepper-content step="17">
              <v-card>
                <v-card-text>
                  <v-list nav dense flat disabled>
                    <v-subheader>Instructions</v-subheader>
                    <v-list-item-group>
                      <v-list-item>
                        <v-list-item-content
                          >• Provide link to data</v-list-item-content
                        >
                      </v-list-item>
                      <v-list-item>
                        <v-list-item-content
                          >• Analyze and download results</v-list-item-content
                        >
                      </v-list-item>
                    </v-list-item-group>
                  </v-list>
                </v-card-text>
                <v-card-actions>
                  <v-btn>
                    Download
                    <v-icon>mdi-download</v-icon>
                  </v-btn>
                </v-card-actions>
              </v-card>
            </v-stepper-content>
            <v-stepper-step editable :complete="workflowStatus.step18" step="18"
              >Cherry-pick successful constructs</v-stepper-step
            >
            <v-stepper-content step="18">
              <v-card>
                <v-card-text>
                  <v-list nav dense flat disabled>
                    <v-subheader>Instructions</v-subheader>
                    <v-list-item-group>
                      <v-list-item>
                        <v-list-item-content
                          >• Download cherry picking
                          instructions</v-list-item-content
                        >
                      </v-list-item>
                      <v-list-item>
                        <v-list-item-content
                          >• Use biomek instructions to cherry pick successful
                          constructs into 2 copies</v-list-item-content
                        >
                      </v-list-item>
                      <v-list-item>
                        <v-list-item-content
                          >• Incubate at 37C overnight</v-list-item-content
                        >
                      </v-list-item>
                      <v-list-item>
                        <v-list-item-content
                          >• Use registry instructions to submit strains to
                          ICE</v-list-item-content
                        >
                      </v-list-item>
                    </v-list-item-group>
                  </v-list>
                </v-card-text>
                <v-card-actions>
                  <v-btn>
                    Download
                    <v-icon>mdi-download</v-icon>
                  </v-btn>
                </v-card-actions>
              </v-card>
            </v-stepper-content>
            <v-stepper-step editable :complete="workflowStatus.step19" step="19"
              >Submit to registry</v-stepper-step
            >
            <v-stepper-content step="19">
              <v-card>
                <v-card-text>
                  <v-list nav dense flat disabled>
                    <v-subheader>Instructions</v-subheader>
                    <v-list-item-group>
                      <v-list-item>
                        <v-list-item-content
                          >• Submit a copy of cultures to physical registry
                          before 10AM</v-list-item-content
                        >
                      </v-list-item>
                      <v-list-item>
                        <v-list-item-content
                          >• Prepare a glycerol stock of cultures for
                          yourself</v-list-item-content
                        >
                      </v-list-item>
                      <v-list-item>
                        <v-list-item-content>• Done :)</v-list-item-content>
                      </v-list-item>
                    </v-list-item-group>
                  </v-list>
                </v-card-text>
              </v-card>
            </v-stepper-content>
          </v-stepper>
        </div>
      </v-card-text>
    </v-card>

    <!-- Dialogs  -->

    <v-dialog v-model="analyzePCRDialog" max-width="600px">
      <v-card>
        <v-card-title>
          <span class="headline">Analyze ZAG Data</span>
        </v-card-title>
        <v-card-text>
          <v-form v-model="validAnalyzeZAGForm" ref="form" lazy-validation>
            <v-file-input
              multiple
              show-size
              accept=".csv"
              label="Upload ZAG Peak Table(s) calculated by ProSize software"
              placeholder="ZAG Peak Table(s)"
              v-model="zagPeakFiles"
              required
            >
              <template v-slot:selection="{ text }">
                <v-chip label small color="primary">{{ text }}</v-chip>
              </template>
            </v-file-input>
            <v-list
              dense
              rounded
              outlined
              subheader
              v-if="zagPeakFiles.length > 1"
            >
              <v-subheader>
                Drag the uploaded peak tables below so that they match their
                correct plate
              </v-subheader>
              <v-list-item-group v-model="zagPeakFiles">
                <draggable
                  v-model="zagPeakFiles"
                  @start="drag = true"
                  @end="drag = false"
                >
                  <v-list-item
                    v-for="element in zagPeakFiles"
                    :key="element.name"
                    class="drag-list-group-item"
                  >
                    <v-list-item-icon>
                      <v-icon>mdi-drag</v-icon>
                    </v-list-item-icon>
                    <v-list-item-content>
                      <v-list-item-title
                        >Plate #{{ zagPeakFiles.indexOf(element) + 1 }}:
                        {{ element.name }}</v-list-item-title
                      >
                    </v-list-item-content>
                  </v-list-item>
                </draggable>
              </v-list-item-group>
            </v-list>
            <v-text-field
              v-model="zagAnalysisSettings.zagColumnPlate"
              name="zagColumnPlate"
              label="Name of Plate column"
              type="text"
            ></v-text-field>
            <v-text-field
              v-model="zagAnalysisSettings.zagColumnWell"
              name="zagColumnWell"
              label="Name of Well column"
              type="text"
            ></v-text-field>
            <v-text-field
              v-model="zagAnalysisSettings.tolerance"
              name="tolerance"
              label="Size Tolerance (0 < tol < 1)"
              type="number"
              max="1"
              min="0"
              step="0.1"
            ></v-text-field>
            <v-select
              v-model="zagAnalysisSettings.polymerase"
              :items="polymeraseOptions"
              label="Polymerase Used"
            ></v-select>
          </v-form>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn @click="cancelAnalyzeZAG">Cancel</v-btn>
          <v-btn @click="resetAnalyzeZAG">Reset</v-btn>
          <v-btn
            @click="submitAnalyzeZAG"
            :disabled="!validAnalyzeZAGForm"
            color="primary"
            >Submit</v-btn
          >
          <v-btn
            @click="downloadAnalyzeZAG"
            :disabled="!activeAnalyzeZAGDownload"
            >Download Result</v-btn
          >
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script lang="ts">
import { Component, Vue, Prop } from 'vue-property-decorator';
import { Store } from 'vuex';
import { readActiveWorkflow } from '@/store/main/getters';
import { dispatchAnalyzePCRs } from '@/store/main/actions';
import { commitSetActiveWorkflow } from '@/store/main/mutations';
import { IUserWorkflow } from '@/interfaces';
import { forceFileDownload } from '@/utils';

@Component
export default class Tab3 extends Vue {
  get activeWorkflow() {
    return readActiveWorkflow(this.$store)(
      +this.$router.currentRoute.params.id
    );
  }

  set activeWorkflow(value: IUserWorkflow) {
    commitSetActiveWorkflow(this.$store, value);
  }

  public workflowStep: string = '1';
  public workflowStatus = {
    step1: false,
    step2: false,
    step3: false,
    step4: false,
    step5: false,
    step6: false,
    step7: false,
    step8: false,
    step9: false,
    step10: false,
    step11: false,
    step12: false,
    step13: false,
    step14: false,
    step15: false,
    step16: false,
    step17: false,
    step18: false,
    step19: false,
  };

  // Variables for Analyze ZAG Standalone
  public analyzePCRDialog: boolean = false;
  public validAnalyzeZAGForm: boolean = false;
  public zagPeakFiles: File[] = [];
  public zagAnalysisSettings = {
    tolerance: '0.50',
    zagColumnPlate: 'OUTPUT_PLATE',
    zagColumnWell: 'OUTPUT_WELL',
    polymerase: 'N/A',
    workflow_id: this.activeWorkflow.id,
  };
  public activeAnalyzeZAGDownload: boolean = false;
  public zagResultsFile: string = '';
  public zagResultsFileName: string = '';
  public polymeraseOptions = ['Q5', 'Phusion GC', 'Phusion HF', 'GXL', 'N/A'];

  // Functions for Analyze ZAG Dialog
  public resetAnalyzeZAG() {
    this.zagPeakFiles = [];
    this.activeAnalyzeZAGDownload = false;
    this.zagResultsFile = '';
    this.zagResultsFileName = '';
    this.zagAnalysisSettings = {
      tolerance: '0.50',
      zagColumnPlate: 'OUTPUT_PLATE',
      zagColumnWell: 'OUTPUT_WELL',
      polymerase: 'N/A',
      workflow_id: this.activeWorkflow.id,
    };
    this.$validator.reset();
  }

  public cancelAnalyzeZAG() {
    this.analyzePCRDialog = false;
    this.resetAnalyzeZAG();
  }

  public async submitAnalyzeZAG() {
    if (await this.$validator.validateAll()) {
      const formData = new FormData();
      for (const element of this.zagPeakFiles) {
        formData.append('peak_files', element, element.name);
      }
      formData.append('settings', JSON.stringify(this.zagAnalysisSettings));
      const response = await dispatchAnalyzePCRs(this.$store, formData);
      if (response === undefined) {
        throw new Error('One of the params must be provided.');
      }
      if (response.data === undefined) {
        throw new Error('One of the params must be provided.');
      }
      const data: any = response.data;
      this.zagResultsFile = data;
      this.zagResultsFileName = 'zag-analysis.csv';
      // console.log(data);
      // forceFileDownload(this.zagResultsFile, this.zagResultsFileName);
      this.activeAnalyzeZAGDownload = true;
    }
  }

  public async downloadAnalyzeZAG() {
    if (this.activeAnalyzeZAGDownload) {
      forceFileDownload(this.zagResultsFile, this.zagResultsFileName);
    }
  }
}
</script>
