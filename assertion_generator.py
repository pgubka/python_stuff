'''
Function to make a simple "test" postman content.

Usage in python console:
> json_string = "json string taken from postman response"
> import assertion_generator as ag
> ag.generate(json_string)

Take the given output and replace values where needed.
Sometimes you'll need
JSON.parse(postman.getEnvironmentVariable()
'''
import json
import string

elist = []

def generate(json_string):
    def assertion_parser(data, assertion_path=''):
        if assertion_path == "" and  not isinstance(data, dict):
            raise Exception('Undefined state for parsing')
        if isinstance(data, dict):
            for k in data.keys():
                assertion_parser(data[k], assertion_path+'["{}"]'.format(k))
        elif isinstance(data, list):
            elist.append((assertion_path, list, len(data)))
            for idx,item in enumerate(data):
                assertion_parser(item, assertion_path+'[{}]'.format(idx))
        elif isinstance(data, str) or isinstance(data, unicode):
            elist.append((assertion_path, str, data))
        elif isinstance(data, int):
            elist.append((assertion_path, int, data))
        elif isinstance(data, bool):
            elist.append((assertion_path, bool, data))
        else:
            raise Exception('Unsupported type: {}, data: {}'.format(type(data), data))

    global elist
    elist = []
    jdata = json.loads(json_string)
    assertion_parser(jdata)

    tstart='''console.log("Response: " + responseBody)

pm.test("Status code is 200", function () {
  pm.response.to.have.status(200);
});'''

    int_bool_templ = '''pm.test("Validate $ELEMENT", function() {
  pm.expect(pm.response.json()$PATH).to.eql($DATA);
});'''
    str_templ = '''pm.test("Validate $ELEMENT", function() {
  pm.expect(pm.response.json()$PATH).to.eql("$DATA");
});'''

    list_count_templ = '''pm.test("Validate $ELEMENT", function() {
  pm.expect(pm.response.json()$PATH.length).to.eql($LEN);
});'''

    
    templa = string.Template(str_templ)
    templb = string.Template(int_bool_templ)
    templc = string.Template(list_count_templ)
    asserts = ["//Use JSON.parse(postman.getEnvironmentVariable(variable name) where needed" ]
    for path, typ, addition in elist:
        if typ == str:
            asserts.append(templa.substitute({'PATH': path, 'ELEMENT': path.split("][")[-1][1:-2], 'DATA': addition}))
        elif typ == list:
            asserts.append(templc.substitute({'PATH': path, 'ELEMENT': path.split("][")[-1][1:-2].replace("\"",""), 'LEN': addition}))
        else:
            asserts.append(templb.substitute({'PATH': path, 'ELEMENT': path.split("][")[-1][1:-2], 'DATA': addition}))
    asserts = "\n".join(asserts)
    print tstart + "\n" + asserts


