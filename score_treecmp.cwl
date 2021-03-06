#!/usr/bin/env cwl-runner
#
# Example score submission file
#
cwlVersion: v1.0
class: CommandLineTool
baseCommand: score.py

hints:
  DockerRequirement:
    dockerPull: sagebionetworks/allen-dream-challenge-scoring:v1

inputs:
  - id: inputfile
    type: File
  - id: goldstandard
    type: File
  - id: runnum
    type: int
  - id: check_validation_finished
    type: boolean?

arguments:
  - valueFrom: $(inputs.inputfile.path)
    prefix: -f
  - valueFrom: $(inputs.goldstandard.path)
    prefix: -g
  - valueFrom: results.json
    prefix: -r
  - valueFrom: '/TreeCmp'
    prefix: -p
  - valueFrom: $(inputs.runnum)
    prefix: -n

requirements:
  - class: InlineJavascriptRequirement
     
outputs:
  - id: results
    type: File
    outputBinding:
      glob: results.json
