"""
Change the specific line in the phil file
"""
def change_phil(file_name:str, reso:str, prefix:str, ref:str):
    with open(file_name, "r") as f:
        line = f.read()
    line = line.replace("merging.d_min=", "merging.d_min=" + reso)
    line = line.replace("output.prefix=", "output.prefix=" + prefix)
    line = line.replace("scaling.model=", "scaling.model=" + ref)
    with open(file_name, "w") as f:
        f.write(line)
