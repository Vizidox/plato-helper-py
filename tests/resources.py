from plato_client_py.api import TemplateInfo

ranger_certificate_template = TemplateInfo(template_id="ranger_certificate",
                                           template_schema={
                                               "properties": {
                                                   "name": {
                                                       "minLength": 1,
                                                       "type": "string"
                                                   },
                                                   "course": {
                                                       "minLength": 1,
                                                       "type": "string"
                                                   }
                                               },
                                               "required": [
                                                   "name",
                                                   "course"
                                               ],
                                               "type": "object"
                                           },
                                           type="text/html",
                                           metadata={"issued_date": "2020-01-01"},
                                           tags=["ranger", "certificate"])

baker_certificate_template = TemplateInfo(template_id="baker_certificate",
                                          template_schema={
                                              "properties": {
                                                  "name": {
                                                      "minLength": 1,
                                                      "type": "string"
                                                  },
                                                  "course": {
                                                      "minLength": 1,
                                                      "type": "string"
                                                  },
                                                  "signature_cake": {
                                                      "minLength": 1,
                                                      "type": "string"
                                                  }
                                              },
                                              "required": [
                                                  "name",
                                                  "course",
                                                  "signature_cake"
                                              ],
                                              "type": "object"
                                          },
                                          type="text/html",
                                          metadata={},
                                          tags=["baker", "certificate"])

ranger_certificate_schema = {
                             "schema": {
                                 "type": "object",
                                 "required": [
                                     "name",
                                     "serial_number",
                                     "course"
                                 ],
                                 "properties": {
                                     "name": {
                                         "type": "string"
                                     },
                                     "serial_number": {
                                         "type": "string"
                                     },
                                     "course": {
                                         "type": "string"
                                     }
                                 }
                             },
                             "type": "text/html",
                             "metadata": {
                             },
                             "example_composition": {
                                 "name": "Charlotte Pine",
                                 "serial_number": "CG-18009",
                                 "course": "Special Ranger Training"
                             },
                             "tags": [
                             ]}

expected_templates = [ranger_certificate_template, baker_certificate_template]
templates_json = [ranger_certificate_template._asdict(), baker_certificate_template._asdict()]
