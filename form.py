import form_parser
import form_intent
import form_completion

# tests.json -> fields.json
form_parser.parse_form()
# fields.json, information.json -> processed_fields.json
form_intent.capture_intent()
# processed_fields.json, information.json -> FORM_FILLED
form_completion.complete_form()
