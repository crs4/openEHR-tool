#test the comparison of two xml files
import sys
sys.path.append('../../')
from myutils import myutils
from lxml import etree

def test_comp_xmls(test_client):
    xml1='''<composition xmlns:ns2="http://schemas.openehr.org/v1" archetype_node_id="openEHR-EHR-COMPOSITION.report.v1">
  <name>
    <value>pippo</value>
  </name>
  <archetype_details>
    <archetype_id>
      <value>openEHR-EHR-COMPOSITION.report.v1</value>
      <qualifiedRmEntity>openEHR-EHR-COMPOSITION</qualifiedRmEntity>
      <domainConcept>report</domainConcept>
      <rmOriginator>openEHR</rmOriginator>
      <rmName>EHR</rmName>
      <rmEntity>COMPOSITION</rmEntity>
      <versionId>1</versionId>
    </archetype_id>
    <template_id>
      <value>pippo</value>
    </template_id>
    <rm_version>1.0.4</rm_version>
  </archetype_details>
  <language>
    <terminology_id>
      <value>ISO_639-1</value>
    </terminology_id>
    <code_string>en</code_string>
  </language>
  <territory>
    <terminology_id>
      <value>ISO_3166-1</value>
    </terminology_id>
    <code_string>ZW</code_string>
  </territory>
  <category>
    <value>event</value>
    <defining_code>
      <terminology_id>
        <value>openehr</value>
      </terminology_id>
      <code_string>433</code_string>
    </defining_code>
  </category>
  <composer xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:type="PARTY_IDENTIFIED">
    <name>EOSC-Life_WP1-DEM</name>
  </composer>
  <context>
    <start_time>
      <value>2022-03-15T12:04:38.490Z</value>
    </start_time>
    <setting>
      <value>other care</value>
      <defining_code>
        <terminology_id>
          <value>openehr</value>
        </terminology_id>
        <code_string>238</code_string>
      </defining_code>
    </setting>
    <other_context xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:type="ITEM_TREE" archetype_node_id="at0001">
      <name>
        <value>Tree</value>
      </name>
      <items xsi:type="CLUSTER" archetype_node_id="openEHR-EHR-CLUSTER.case_identification.v0">
        <name>
          <value>Case identification</value>
        </name>
        <items xsi:type="ELEMENT" archetype_node_id="at0001">
          <name>
            <value>Patient pseudonym</value>
          </name>
          <value xsi:type="DV_TEXT">
            <value>1749123</value>
          </value>
        </items>
        <items xsi:type="ELEMENT" archetype_node_id="at0006">
          <name>
            <value>Participation in clinical study</value>
          </name>
          <value xsi:type="DV_TEXT">
            <value>FALSE</value>
          </value>
        </items>
      </items>
    </other_context>
  </context>
  <content xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:type="SECTION" archetype_node_id="openEHR-EHR-SECTION.adhoc.v1">
    <name>
      <value>Sample</value>
    </name>
    <items xsi:type="EVALUATION" archetype_node_id="openEHR-EHR-EVALUATION.biospecimen_summary.v0">
      <name>
        <value>Biospecimen summary</value>
      </name>
      <archetype_details>
        <archetype_id>
          <value>openEHR-EHR-EVALUATION.biospecimen_summary.v0</value>
          <qualifiedRmEntity>openEHR-EHR-EVALUATION</qualifiedRmEntity>
          <domainConcept>biospecimen_summary</domainConcept>
          <rmOriginator>openEHR</rmOriginator>
          <rmName>EHR</rmName>
          <rmEntity>EVALUATION</rmEntity>
          <versionId>0</versionId>
        </archetype_id>
        <template_id>
          <value>pippo</value>
        </template_id>
        <rm_version>1.0.4</rm_version>
      </archetype_details>
      <language>
        <terminology_id>
          <value>ISO_639-1</value>
        </terminology_id>
        <code_string>en</code_string>
      </language>
      <encoding>
        <terminology_id>
          <value>IANA_character-sets</value>
        </terminology_id>
        <code_string>UTF-8</code_string>
      </encoding>
      <subject xsi:type="PARTY_SELF"/>
      <data xsi:type="ITEM_TREE" archetype_node_id="at0001">
        <name>
          <value>Item tree</value>
        </name>
        <items xsi:type="ELEMENT" archetype_node_id="at0002">
          <name>
            <value>Sample ID</value>
          </name>
          <value xsi:type="DV_IDENTIFIER">
            <issuer>unknown</issuer>
            <assigner>unknown</assigner>
            <id>557</id>
            <type>unknown</type>
          </value>
        </items>
        <items xsi:type="ELEMENT" archetype_node_id="at0003">
          <name>
            <value>Material type</value>
          </name>
          <value xsi:type="DV_CODED_TEXT">
            <value>Tumor tissue sample</value>
            <defining_code>
              <terminology_id>
                <value>omop_vocabulary</value>
              </terminology_id>
              <code_string>4122248</code_string>
            </defining_code>
          </value>
        </items>
        <items xsi:type="ELEMENT" archetype_node_id="at0007">
          <name>
            <value>Preservation mode</value>
          </name>
          <value xsi:type="DV_CODED_TEXT">
            <value>FFPE</value>
            <defining_code>
              <terminology_id>
                <value>omop_vocabulary</value>
              </terminology_id>
              <code_string>37206850</code_string>
            </defining_code>
          </value>
        </items>
        <items xsi:type="CLUSTER" archetype_node_id="openEHR-EHR-CLUSTER.specimen.v1">
          <name>
            <value>Specimen</value>
          </name>
          <items xsi:type="ELEMENT" archetype_node_id="at0015">
            <name>
              <value>Year of sample collection</value>
            </name>
            <value xsi:type="DV_DATE_TIME">
              <value>2022-01-01T00:00Z</value>
            </value>
          </items>
        </items>
      </data>
    </items>
  </content>
  <content xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:type="SECTION" archetype_node_id="openEHR-EHR-SECTION.adhoc.v1">
    <name>
      <value>Surgery</value>
    </name>
    <items xsi:type="ACTION" archetype_node_id="openEHR-EHR-ACTION.procedure.v1">
      <name>
        <value>Surgery</value>
      </name>
      <archetype_details>
        <archetype_id>
          <value>openEHR-EHR-ACTION.procedure.v1</value>
          <qualifiedRmEntity>openEHR-EHR-ACTION</qualifiedRmEntity>
          <domainConcept>procedure</domainConcept>
          <rmOriginator>openEHR</rmOriginator>
          <rmName>EHR</rmName>
          <rmEntity>ACTION</rmEntity>
          <versionId>1</versionId>
        </archetype_id>
        <template_id>
          <value>pippo</value>
        </template_id>
        <rm_version>1.0.4</rm_version>
      </archetype_details>
      <language>
        <terminology_id>
          <value>ISO_639-1</value>
        </terminology_id>
        <code_string>en</code_string>
      </language>
      <encoding>
        <terminology_id>
          <value>IANA_character-sets</value>
        </terminology_id>
        <code_string>UTF-8</code_string>
      </encoding>
      <subject xsi:type="PARTY_SELF"/>
      <time>
        <value>2018-11-07T00:00Z</value>
      </time>
      <description xsi:type="ITEM_TREE" archetype_node_id="at0001">
        <name>
          <value>Tree</value>
        </name>
        <items xsi:type="ELEMENT" archetype_node_id="at0002">
          <name>
            <value>Surgery type</value>
          </name>
          <value xsi:type="DV_CODED_TEXT">
            <value>Anterior resection of rectum</value>
            <defining_code>
              <terminology_id>
                <value>omop_vocabulary</value>
              </terminology_id>
              <code_string>4166855</code_string>
            </defining_code>
          </value>
        </items>
        <items xsi:type="ELEMENT" archetype_node_id="at0048">
          <name>
            <value>Surgery radicality</value>
          </name>
          <value xsi:type="DV_CODED_TEXT">
            <value>R2</value>
            <defining_code>
              <terminology_id>
                <value>omop_vocabulary</value>
              </terminology_id>
              <code_string>4121182</code_string>
            </defining_code>
          </value>
        </items>
        <items xsi:type="ELEMENT" archetype_node_id="at0063">
          <name>
            <value>Location of the tumor</value>
          </name>
          <value xsi:type="DV_CODED_TEXT">
            <value>C 20 - Rectum</value>
            <defining_code>
              <terminology_id>
                <value>omop_vocabulary</value>
              </terminology_id>
              <code_string>74582</code_string>
            </defining_code>
          </value>
        </items>
        <items xsi:type="CLUSTER" archetype_node_id="openEHR-EHR-CLUSTER.timing_nondaily.v1">
          <name>
            <value>Surgery timing</value>
          </name>
          <items xsi:type="CLUSTER" archetype_node_id="at0006">
            <name>
              <value>Surgery</value>
            </name>
            <items xsi:type="ELEMENT" archetype_node_id="at0005">
              <name>
                <value>From event</value>
              </name>
              <value xsi:type="DV_TEXT">
                <value>Primary diagnosis</value>
              </value>
            </items>
            <items xsi:type="ELEMENT" archetype_node_id="at0009">
              <name>
                <value>Surgery start relative</value>
              </name>
              <value xsi:type="DV_DURATION">
                <value>P1W</value>
              </value>
            </items>
          </items>
        </items>
      </description>
      <ism_transition>
        <current_state>
          <value>completed</value>
          <defining_code>
            <terminology_id>
              <value>openehr</value>
            </terminology_id>
            <code_string>532</code_string>
          </defining_code>
        </current_state>
      </ism_transition>
    </items>
  </content>
  <content xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:type="SECTION" archetype_node_id="openEHR-EHR-SECTION.adhoc.v1">
    <name>
      <value>Diagnostic examinations</value>
    </name>
    <items xsi:type="ACTION" archetype_node_id="openEHR-EHR-ACTION.procedure.v1">
      <name>
        <value>Colonoscopy</value>
      </name>
      <archetype_details>
        <archetype_id>
          <value>openEHR-EHR-ACTION.procedure.v1</value>
          <qualifiedRmEntity>openEHR-EHR-ACTION</qualifiedRmEntity>
          <domainConcept>procedure</domainConcept>
          <rmOriginator>openEHR</rmOriginator>
          <rmName>EHR</rmName>
          <rmEntity>ACTION</rmEntity>
          <versionId>1</versionId>
        </archetype_id>
        <template_id>
          <value>pippo</value>
        </template_id>
        <rm_version>1.0.4</rm_version>
      </archetype_details>
      <language>
        <terminology_id>
          <value>ISO_639-1</value>
        </terminology_id>
        <code_string>en</code_string>
      </language>
      <encoding>
        <terminology_id>
          <value>IANA_character-sets</value>
        </terminology_id>
        <code_string>UTF-8</code_string>
      </encoding>
      <subject xsi:type="PARTY_SELF"/>
      <time>
        <value>9999-12-10T00:00Z</value>
      </time>
      <description xsi:type="ITEM_TREE" archetype_node_id="at0001">
        <name>
          <value>Tree</value>
        </name>
        <items xsi:type="ELEMENT" archetype_node_id="at0002">
          <name>
            <value>Procedure name</value>
          </name>
          <value xsi:type="DV_TEXT">
            <value>Colonoscopy</value>
          </value>
        </items>
        <items xsi:type="ELEMENT" archetype_node_id="at0048">
          <name>
            <value>Colonoscopy</value>
          </name>
          <value xsi:type="DV_TEXT">
            <value>Not done</value>
          </value>
        </items>
      </description>
      <ism_transition>
        <current_state>
          <value>completed</value>
          <defining_code>
            <terminology_id>
              <value>openehr</value>
            </terminology_id>
            <code_string>532</code_string>
          </defining_code>
        </current_state>
      </ism_transition>
    </items>
    <items xsi:type="ACTION" archetype_node_id="openEHR-EHR-ACTION.procedure.v1">
      <name>
        <value>CT</value>
      </name>
      <archetype_details>
        <archetype_id>
          <value>openEHR-EHR-ACTION.procedure.v1</value>
          <qualifiedRmEntity>openEHR-EHR-ACTION</qualifiedRmEntity>
          <domainConcept>procedure</domainConcept>
          <rmOriginator>openEHR</rmOriginator>
          <rmName>EHR</rmName>
          <rmEntity>ACTION</rmEntity>
          <versionId>1</versionId>
        </archetype_id>
        <template_id>
          <value>pippo</value>
        </template_id>
        <rm_version>1.0.4</rm_version>
      </archetype_details>
      <language>
        <terminology_id>
          <value>ISO_639-1</value>
        </terminology_id>
        <code_string>en</code_string>
      </language>
      <encoding>
        <terminology_id>
          <value>IANA_character-sets</value>
        </terminology_id>
        <code_string>UTF-8</code_string>
      </encoding>
      <subject xsi:type="PARTY_SELF"/>
      <time>
        <value>9999-12-10T00:00Z</value>
      </time>
      <description xsi:type="ITEM_TREE" archetype_node_id="at0001">
        <name>
          <value>Tree</value>
        </name>
        <items xsi:type="ELEMENT" archetype_node_id="at0002">
          <name>
            <value>Procedure name</value>
          </name>
          <value xsi:type="DV_TEXT">
            <value>CT</value>
          </value>
        </items>
        <items xsi:type="ELEMENT" archetype_node_id="at0048">
          <name>
            <value>CT</value>
          </name>
          <value xsi:type="DV_TEXT">
            <value>Done, data available</value>
          </value>
        </items>
      </description>
      <ism_transition>
        <current_state>
          <value>completed</value>
          <defining_code>
            <terminology_id>
              <value>openehr</value>
            </terminology_id>
            <code_string>532</code_string>
          </defining_code>
        </current_state>
      </ism_transition>
    </items>
    <items xsi:type="ACTION" archetype_node_id="openEHR-EHR-ACTION.procedure.v1">
      <name>
        <value>Liver imaging</value>
      </name>
      <archetype_details>
        <archetype_id>
          <value>openEHR-EHR-ACTION.procedure.v1</value>
          <qualifiedRmEntity>openEHR-EHR-ACTION</qualifiedRmEntity>
          <domainConcept>procedure</domainConcept>
          <rmOriginator>openEHR</rmOriginator>
          <rmName>EHR</rmName>
          <rmEntity>ACTION</rmEntity>
          <versionId>1</versionId>
        </archetype_id>
        <template_id>
          <value>pippo</value>
        </template_id>
        <rm_version>1.0.4</rm_version>
      </archetype_details>
      <language>
        <terminology_id>
          <value>ISO_639-1</value>
        </terminology_id>
        <code_string>en</code_string>
      </language>
      <encoding>
        <terminology_id>
          <value>IANA_character-sets</value>
        </terminology_id>
        <code_string>UTF-8</code_string>
      </encoding>
      <subject xsi:type="PARTY_SELF"/>
      <time>
        <value>9999-12-10T00:00Z</value>
      </time>
      <description xsi:type="ITEM_TREE" archetype_node_id="at0001">
        <name>
          <value>Tree</value>
        </name>
        <items xsi:type="ELEMENT" archetype_node_id="at0002">
          <name>
            <value>Procedure name</value>
          </name>
          <value xsi:type="DV_TEXT">
            <value>Liver imaging</value>
          </value>
        </items>
        <items xsi:type="ELEMENT" archetype_node_id="at0048">
          <name>
            <value>Liver imaging</value>
          </name>
          <value xsi:type="DV_TEXT">
            <value>Done, data available</value>
          </value>
        </items>
      </description>
      <ism_transition>
        <current_state>
          <value>completed</value>
          <defining_code>
            <terminology_id>
              <value>openehr</value>
            </terminology_id>
            <code_string>532</code_string>
          </defining_code>
        </current_state>
      </ism_transition>
    </items>
    <items xsi:type="ACTION" archetype_node_id="openEHR-EHR-ACTION.procedure.v1">
      <name>
        <value>Lung imaging</value>
      </name>
      <archetype_details>
        <archetype_id>
          <value>openEHR-EHR-ACTION.procedure.v1</value>
          <qualifiedRmEntity>openEHR-EHR-ACTION</qualifiedRmEntity>
          <domainConcept>procedure</domainConcept>
          <rmOriginator>openEHR</rmOriginator>
          <rmName>EHR</rmName>
          <rmEntity>ACTION</rmEntity>
          <versionId>1</versionId>
        </archetype_id>
        <template_id>
          <value>pippo</value>
        </template_id>
        <rm_version>1.0.4</rm_version>
      </archetype_details>
      <language>
        <terminology_id>
          <value>ISO_639-1</value>
        </terminology_id>
        <code_string>en</code_string>
      </language>
      <encoding>
        <terminology_id>
          <value>IANA_character-sets</value>
        </terminology_id>
        <code_string>UTF-8</code_string>
      </encoding>
      <subject xsi:type="PARTY_SELF"/>
      <time>
        <value>9999-12-10T00:00Z</value>
      </time>
      <description xsi:type="ITEM_TREE" archetype_node_id="at0001">
        <name>
          <value>Tree</value>
        </name>
        <items xsi:type="ELEMENT" archetype_node_id="at0002">
          <name>
            <value>Procedure name</value>
          </name>
          <value xsi:type="DV_TEXT">
            <value>Lung imaging</value>
          </value>
        </items>
        <items xsi:type="ELEMENT" archetype_node_id="at0048">
          <name>
            <value>Lung imaging</value>
          </name>
          <value xsi:type="DV_TEXT">
            <value>Done, data available</value>
          </value>
        </items>
      </description>
      <ism_transition>
        <current_state>
          <value>completed</value>
          <defining_code>
            <terminology_id>
              <value>openehr</value>
            </terminology_id>
            <code_string>532</code_string>
          </defining_code>
        </current_state>
      </ism_transition>
    </items>
    <items xsi:type="ACTION" archetype_node_id="openEHR-EHR-ACTION.procedure.v1">
      <name>
        <value>MRI</value>
      </name>
      <archetype_details>
        <archetype_id>
          <value>openEHR-EHR-ACTION.procedure.v1</value>
          <qualifiedRmEntity>openEHR-EHR-ACTION</qualifiedRmEntity>
          <domainConcept>procedure</domainConcept>
          <rmOriginator>openEHR</rmOriginator>
          <rmName>EHR</rmName>
          <rmEntity>ACTION</rmEntity>
          <versionId>1</versionId>
        </archetype_id>
        <template_id>
          <value>pippo</value>
        </template_id>
        <rm_version>1.0.4</rm_version>
      </archetype_details>
      <language>
        <terminology_id>
          <value>ISO_639-1</value>
        </terminology_id>
        <code_string>en</code_string>
      </language>
      <encoding>
        <terminology_id>
          <value>IANA_character-sets</value>
        </terminology_id>
        <code_string>UTF-8</code_string>
      </encoding>
      <subject xsi:type="PARTY_SELF"/>
      <time>
        <value>9999-12-10T00:00Z</value>
      </time>
      <description xsi:type="ITEM_TREE" archetype_node_id="at0001">
        <name>
          <value>Tree</value>
        </name>
        <items xsi:type="ELEMENT" archetype_node_id="at0002">
          <name>
            <value>Procedure name</value>
          </name>
          <value xsi:type="DV_TEXT">
            <value>MRI</value>
          </value>
        </items>
        <items xsi:type="ELEMENT" archetype_node_id="at0048">
          <name>
            <value>MRI</value>
          </name>
          <value xsi:type="DV_TEXT">
            <value>Unknown</value>
          </value>
        </items>
      </description>
      <ism_transition>
        <current_state>
          <value>completed</value>
          <defining_code>
            <terminology_id>
              <value>openehr</value>
            </terminology_id>
            <code_string>532</code_string>
          </defining_code>
        </current_state>
      </ism_transition>
    </items>
  </content>
  <content xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:type="SECTION" archetype_node_id="openEHR-EHR-SECTION.adhoc.v1">
    <name>
      <value>Vital status and survival information</value>
    </name>
    <items xsi:type="EVALUATION" archetype_node_id="openEHR-EHR-EVALUATION.clinical_synopsis.v1">
      <name>
        <value>Vital status and survival information</value>
      </name>
      <archetype_details>
        <archetype_id>
          <value>openEHR-EHR-EVALUATION.clinical_synopsis.v1</value>
          <qualifiedRmEntity>openEHR-EHR-EVALUATION</qualifiedRmEntity>
          <domainConcept>clinical_synopsis</domainConcept>
          <rmOriginator>openEHR</rmOriginator>
          <rmName>EHR</rmName>
          <rmEntity>EVALUATION</rmEntity>
          <versionId>1</versionId>
        </archetype_id>
        <template_id>
          <value>pippo</value>
        </template_id>
        <rm_version>1.0.4</rm_version>
      </archetype_details>
      <language>
        <terminology_id>
          <value>ISO_639-1</value>
        </terminology_id>
        <code_string>en</code_string>
      </language>
      <encoding>
        <terminology_id>
          <value>IANA_character-sets</value>
        </terminology_id>
        <code_string>UTF-8</code_string>
      </encoding>
      <subject xsi:type="PARTY_SELF"/>
      <protocol xsi:type="ITEM_TREE" archetype_node_id="at0003">
        <name>
          <value>Tree</value>
        </name>
        <items xsi:type="CLUSTER" archetype_node_id="openEHR-EHR-CLUSTER.timing_nondaily.v1">
          <name>
            <value>Vital status timing</value>
          </name>
          <items xsi:type="ELEMENT" archetype_node_id="at0001">
            <name>
              <value>Timestamp of last update of vital status</value>
            </name>
            <value xsi:type="DV_DATE">
              <value>2002-04-01</value>
            </value>
          </items>
          <items xsi:type="CLUSTER" archetype_node_id="at0006">
            <name>
              <value>Overall survival status</value>
            </name>
            <items xsi:type="ELEMENT" archetype_node_id="at0005">
              <name>
                <value>From event</value>
              </name>
              <value xsi:type="DV_TEXT">
                <value>First colon cancer therapy</value>
              </value>
            </items>
            <items xsi:type="ELEMENT" archetype_node_id="at0009">
              <name>
                <value>Overall survival status</value>
              </name>
              <value xsi:type="DV_DURATION">
                <value>P65W</value>
              </value>
            </items>
          </items>
        </items>
      </protocol>
      <data xsi:type="ITEM_TREE" archetype_node_id="at0001">
        <name>
          <value>List</value>
        </name>
        <items xsi:type="ELEMENT" archetype_node_id="at0002">
          <name>
            <value>Vital status</value>
          </name>
          <value xsi:type="DV_TEXT">
            <value>death for unknown reasons</value>
          </value>
        </items>
      </data>
    </items>
  </content>
  <content xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:type="SECTION" archetype_node_id="openEHR-EHR-SECTION.result_details.v0">
    <name>
      <value>Histopathology</value>
    </name>
    <items xsi:type="SECTION" archetype_node_id="at0002">
      <name>
        <value>Result group</value>
      </name>
      <items xsi:type="EVALUATION" archetype_node_id="openEHR-EHR-EVALUATION.problem_diagnosis.v1">
        <name>
          <value>Cancer diagnosis</value>
        </name>
        <archetype_details>
          <archetype_id>
            <value>openEHR-EHR-EVALUATION.problem_diagnosis.v1</value>
            <qualifiedRmEntity>openEHR-EHR-EVALUATION</qualifiedRmEntity>
            <domainConcept>problem_diagnosis</domainConcept>
            <rmOriginator>openEHR</rmOriginator>
            <rmName>EHR</rmName>
            <rmEntity>EVALUATION</rmEntity>
            <versionId>1</versionId>
          </archetype_id>
          <template_id>
            <value>pippo</value>
          </template_id>
          <rm_version>1.0.4</rm_version>
        </archetype_details>
        <language>
          <terminology_id>
            <value>ISO_639-1</value>
          </terminology_id>
          <code_string>en</code_string>
        </language>
        <encoding>
          <terminology_id>
            <value>IANA_character-sets</value>
          </terminology_id>
          <code_string>UTF-8</code_string>
        </encoding>
        <subject xsi:type="PARTY_SELF"/>
        <data xsi:type="ITEM_TREE" archetype_node_id="at0001">
          <name>
            <value>structure</value>
          </name>
          <items xsi:type="ELEMENT" archetype_node_id="at0002">
            <name>
              <value>Problem/Diagnosis name</value>
            </name>
            <value xsi:type="DV_CODED_TEXT">
              <value>Colorectal cancer</value>
              <defining_code>
                <terminology_id>
                  <value>omop_vocabulary</value>
                </terminology_id>
                <code_string>44803809</code_string>
              </defining_code>
            </value>
          </items>
          <items xsi:type="ELEMENT" archetype_node_id="at0012">
            <name>
              <value>Localization of primary tumor</value>
            </name>
            <value xsi:type="DV_CODED_TEXT">
              <value>C 20 - Rectum</value>
              <defining_code>
                <terminology_id>
                  <value>omop_vocabulary</value>
                </terminology_id>
                <code_string>74582</code_string>
              </defining_code>
            </value>
          </items>
          <items xsi:type="CLUSTER" archetype_node_id="openEHR-EHR-CLUSTER.synoptic_details_colorectal_carcinoma.v0">
            <name>
              <value>Synoptic details - Colorectal cancer</value>
            </name>
            <items xsi:type="CLUSTER" archetype_node_id="at0001">
              <name>
                <value>Microscopic findings</value>
              </name>
              <items xsi:type="ELEMENT" archetype_node_id="at0033">
                <name>
                  <value>Morphology</value>
                </name>
                <value xsi:type="DV_CODED_TEXT">
                  <value>Adenocarcinoma</value>
                  <defining_code>
                    <terminology_id>
                      <value>omop_vocabulary</value>
                    </terminology_id>
                    <code_string>42530737</code_string>
                  </defining_code>
                </value>
              </items>
              <items xsi:type="CLUSTER" archetype_node_id="at0263">
                <name>
                  <value>Distant metastasis</value>
                </name>
                <items xsi:type="CLUSTER" archetype_node_id="openEHR-EHR-CLUSTER.anatomical_location.v1">
                  <name>
                    <value>Anatomical location</value>
                  </name>
                  <items xsi:type="ELEMENT" archetype_node_id="at0001">
                    <name>
                      <value>Localization of metastasis</value>
                    </name>
                    <value xsi:type="DV_CODED_TEXT">
                      <value>Lymph Nodes</value>
                      <defining_code>
                        <terminology_id>
                          <value>omop_vocabulary</value>
                        </terminology_id>
                        <code_string>45881859</code_string>
                      </defining_code>
                    </value>
                  </items>
                </items>
              </items>
              <items xsi:type="CLUSTER" archetype_node_id="at0269">
                <name>
                  <value>Histological grading</value>
                </name>
                <items xsi:type="ELEMENT" archetype_node_id="at0271">
                  <name>
                    <value>WHO version</value>
                  </name>
                  <value xsi:type="DV_TEXT">
                    <value>2nd ed. (1991- 2000)</value>
                  </value>
                </items>
              </items>
              <items xsi:type="CLUSTER" archetype_node_id="openEHR-EHR-CLUSTER.tnm-pathological.v1">
                <name>
                  <value>TNM pathological classification</value>
                </name>
                <items xsi:type="ELEMENT" archetype_node_id="at0006">
                  <name>
                    <value>Grade</value>
                  </name>
                  <value xsi:type="DV_CODED_TEXT">
                    <value>G3</value>
                    <defining_code>
                      <terminology_id>
                        <value>omop_vocabulary</value>
                      </terminology_id>
                      <code_string>36769033</code_string>
                    </defining_code>
                  </value>
                </items>
                <items xsi:type="ELEMENT" archetype_node_id="at0032">
                  <name>
                    <value>UICC version</value>
                  </name>
                  <value xsi:type="DV_TEXT">
                    <value>5th. ed (used 1998-2002)</value>
                  </value>
                </items>
                <items xsi:type="ELEMENT" archetype_node_id="at0003.1">
                  <name>
                    <value>Primary tumour</value>
                  </name>
                  <value xsi:type="DV_CODED_TEXT">
                    <value>T3</value>
                    <defining_code>
                      <terminology_id>
                        <value>omop_vocabulary</value>
                      </terminology_id>
                      <code_string>4234703</code_string>
                    </defining_code>
                  </value>
                </items>
                <items xsi:type="ELEMENT" archetype_node_id="at0004.1">
                  <name>
                    <value>Regional lymph nodes</value>
                  </name>
                  <value xsi:type="DV_CODED_TEXT">
                    <value>N2</value>
                    <defining_code>
                      <terminology_id>
                        <value>omop_vocabulary</value>
                      </terminology_id>
                      <code_string>45881614</code_string>
                    </defining_code>
                  </value>
                </items>
                <items xsi:type="ELEMENT" archetype_node_id="at0005.1">
                  <name>
                    <value>Distant metastasis</value>
                  </name>
                  <value xsi:type="DV_CODED_TEXT">
                    <value>MX</value>
                    <defining_code>
                      <terminology_id>
                        <value>omop_vocabulary</value>
                      </terminology_id>
                      <code_string>45876323</code_string>
                    </defining_code>
                  </value>
                </items>
                <items xsi:type="ELEMENT" archetype_node_id="at0031.1">
                  <name>
                    <value>Stage</value>
                  </name>
                  <value xsi:type="DV_CODED_TEXT">
                    <value>Stage - III</value>
                    <defining_code>
                      <terminology_id>
                        <value>omop_vocabulary</value>
                      </terminology_id>
                      <code_string>45878643</code_string>
                    </defining_code>
                  </value>
                </items>
              </items>
            </items>
          </items>
        </data>
      </items>
      <items xsi:type="OBSERVATION" archetype_node_id="openEHR-EHR-OBSERVATION.laboratory_test_result.v1">
        <name>
          <value>Laboratory test result</value>
        </name>
        <archetype_details>
          <archetype_id>
            <value>openEHR-EHR-OBSERVATION.laboratory_test_result.v1</value>
            <qualifiedRmEntity>openEHR-EHR-OBSERVATION</qualifiedRmEntity>
            <domainConcept>laboratory_test_result</domainConcept>
            <rmOriginator>openEHR</rmOriginator>
            <rmName>EHR</rmName>
            <rmEntity>OBSERVATION</rmEntity>
            <versionId>1</versionId>
          </archetype_id>
          <template_id>
            <value>pippo</value>
          </template_id>
          <rm_version>1.0.4</rm_version>
        </archetype_details>
        <language>
          <terminology_id>
            <value>ISO_639-1</value>
          </terminology_id>
          <code_string>en</code_string>
        </language>
        <encoding>
          <terminology_id>
            <value>IANA_character-sets</value>
          </terminology_id>
          <code_string>UTF-8</code_string>
        </encoding>
        <subject xsi:type="PARTY_SELF"/>
        <data archetype_node_id="at0001">
          <name>
            <value>Event Series</value>
          </name>
          <origin>
            <value>2018-11-07T00:00Z</value>
          </origin>
          <events xsi:type="POINT_EVENT" archetype_node_id="at0002">
            <name>
              <value>Any event</value>
            </name>
            <time>
              <value>2018-11-07T00:00Z</value>
            </time>
            <data xsi:type="ITEM_TREE" archetype_node_id="at0003">
              <name>
                <value>Tree</value>
              </name>
              <items xsi:type="ELEMENT" archetype_node_id="at0005">
                <name>
                  <value>Test name</value>
                </name>
                <value xsi:type="DV_TEXT">
                  <value>Histopathology analysis</value>
                </value>
              </items>
              <items xsi:type="CLUSTER" archetype_node_id="openEHR-EHR-CLUSTER.anatomical_pathology_exam.v0">
                <name>
                  <value>Anatomical pathology examination</value>
                </name>
                <items xsi:type="CLUSTER" archetype_node_id="at0005">
                  <name>
                    <value>Anatomical pathology finding</value>
                  </name>
                  <items xsi:type="CLUSTER" archetype_node_id="openEHR-EHR-CLUSTER.media_file.v1">
                    <name>
                      <value>Media file</value>
                    </name>
                    <items xsi:type="ELEMENT" archetype_node_id="at0007">
                      <name>
                        <value>Availability digital imaging</value>
                      </name>
                      <value xsi:type="DV_TEXT">
                        <value>Can be generated</value>
                      </value>
                    </items>
                  </items>
                </items>
              </items>
              <items xsi:type="CLUSTER" archetype_node_id="openEHR-EHR-CLUSTER.anatomical_pathology_exam.v0">
                <name>
                  <value>Invasion front</value>
                </name>
                <items xsi:type="CLUSTER" archetype_node_id="at0005">
                  <name>
                    <value>Anatomical pathology finding</value>
                  </name>
                  <items xsi:type="CLUSTER" archetype_node_id="openEHR-EHR-CLUSTER.media_file.v1">
                    <name>
                      <value>Digital imaging invasion front</value>
                    </name>
                    <items xsi:type="ELEMENT" archetype_node_id="at0007">
                      <name>
                        <value>Availability invasion front digital imaging</value>
                      </name>
                      <value xsi:type="DV_TEXT">
                        <value>Can be generated</value>
                      </value>
                    </items>
                  </items>
                </items>
              </items>
            </data>
          </events>
        </data>
      </items>
    </items>
  </content>
  <content xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:type="SECTION" archetype_node_id="openEHR-EHR-SECTION.result_details.v0">
    <name>
      <value>Molecular markers</value>
    </name>
    <items xsi:type="SECTION" archetype_node_id="at0002">
      <name>
        <value>Result group</value>
      </name>
      <items xsi:type="OBSERVATION" archetype_node_id="openEHR-EHR-OBSERVATION.laboratory_test_result.v1">
        <name>
          <value>Oncogenic mutations test</value>
        </name>
        <archetype_details>
          <archetype_id>
            <value>openEHR-EHR-OBSERVATION.laboratory_test_result.v1</value>
            <qualifiedRmEntity>openEHR-EHR-OBSERVATION</qualifiedRmEntity>
            <domainConcept>laboratory_test_result</domainConcept>
            <rmOriginator>openEHR</rmOriginator>
            <rmName>EHR</rmName>
            <rmEntity>OBSERVATION</rmEntity>
            <versionId>1</versionId>
          </archetype_id>
          <template_id>
            <value>pippo</value>
          </template_id>
          <rm_version>1.0.4</rm_version>
        </archetype_details>
        <language>
          <terminology_id>
            <value>ISO_639-1</value>
          </terminology_id>
          <code_string>en</code_string>
        </language>
        <encoding>
          <terminology_id>
            <value>IANA_character-sets</value>
          </terminology_id>
          <code_string>UTF-8</code_string>
        </encoding>
        <subject xsi:type="PARTY_SELF"/>
        <data archetype_node_id="at0001">
          <name>
            <value>Event Series</value>
          </name>
          <origin>
            <value>9999-12-10T00:00Z</value>
          </origin>
          <events xsi:type="POINT_EVENT" archetype_node_id="at0002">
            <name>
              <value>Any event</value>
            </name>
            <time>
              <value>9999-12-10T00:00Z</value>
            </time>
            <data xsi:type="ITEM_TREE" archetype_node_id="at0003">
              <name>
                <value>Tree</value>
              </name>
              <items xsi:type="ELEMENT" archetype_node_id="at0005">
                <name>
                  <value>Test name</value>
                </name>
                <value xsi:type="DV_TEXT">
                  <value>BRAF, PIC3CA, HER2 mutation test</value>
                </value>
              </items>
              <items xsi:type="ELEMENT" archetype_node_id="at0057">
                <name>
                  <value>BRAF, PIC3CA, HER2 mutation status</value>
                </name>
                <value xsi:type="DV_TEXT">
                  <value>Not done</value>
                </value>
              </items>
            </data>
          </events>
        </data>
      </items>
      <items xsi:type="OBSERVATION" archetype_node_id="openEHR-EHR-OBSERVATION.laboratory_test_result.v1">
        <name>
          <value>Microsatellites instability analysis</value>
        </name>
        <archetype_details>
          <archetype_id>
            <value>openEHR-EHR-OBSERVATION.laboratory_test_result.v1</value>
            <qualifiedRmEntity>openEHR-EHR-OBSERVATION</qualifiedRmEntity>
            <domainConcept>laboratory_test_result</domainConcept>
            <rmOriginator>openEHR</rmOriginator>
            <rmName>EHR</rmName>
            <rmEntity>OBSERVATION</rmEntity>
            <versionId>1</versionId>
          </archetype_id>
          <template_id>
            <value>pippo</value>
          </template_id>
          <rm_version>1.0.4</rm_version>
        </archetype_details>
        <language>
          <terminology_id>
            <value>ISO_639-1</value>
          </terminology_id>
          <code_string>en</code_string>
        </language>
        <encoding>
          <terminology_id>
            <value>IANA_character-sets</value>
          </terminology_id>
          <code_string>UTF-8</code_string>
        </encoding>
        <subject xsi:type="PARTY_SELF"/>
        <data archetype_node_id="at0001">
          <name>
            <value>Event Series</value>
          </name>
          <origin>
            <value>9999-12-10T00:00Z</value>
          </origin>
          <events xsi:type="POINT_EVENT" archetype_node_id="at0002">
            <name>
              <value>Any event</value>
            </name>
            <time>
              <value>9999-12-10T00:00Z</value>
            </time>
            <data xsi:type="ITEM_TREE" archetype_node_id="at0003">
              <name>
                <value>Tree</value>
              </name>
              <items xsi:type="ELEMENT" archetype_node_id="at0005">
                <name>
                  <value>Test name</value>
                </name>
                <value xsi:type="DV_TEXT">
                  <value>Microsatellite instability test</value>
                </value>
              </items>
              <items xsi:type="ELEMENT" archetype_node_id="at0057">
                <name>
                  <value>Microsatellite instability</value>
                </name>
                <value xsi:type="DV_TEXT">
                  <value>Not done</value>
                </value>
              </items>
            </data>
          </events>
        </data>
      </items>
      <items xsi:type="OBSERVATION" archetype_node_id="openEHR-EHR-OBSERVATION.laboratory_test_result.v1">
        <name>
          <value>KRAS mutation status</value>
        </name>
        <archetype_details>
          <archetype_id>
            <value>openEHR-EHR-OBSERVATION.laboratory_test_result.v1</value>
            <qualifiedRmEntity>openEHR-EHR-OBSERVATION</qualifiedRmEntity>
            <domainConcept>laboratory_test_result</domainConcept>
            <rmOriginator>openEHR</rmOriginator>
            <rmName>EHR</rmName>
            <rmEntity>OBSERVATION</rmEntity>
            <versionId>1</versionId>
          </archetype_id>
          <template_id>
            <value>pippo</value>
          </template_id>
          <rm_version>1.0.4</rm_version>
        </archetype_details>
        <language>
          <terminology_id>
            <value>ISO_639-1</value>
          </terminology_id>
          <code_string>en</code_string>
        </language>
        <encoding>
          <terminology_id>
            <value>IANA_character-sets</value>
          </terminology_id>
          <code_string>UTF-8</code_string>
        </encoding>
        <subject xsi:type="PARTY_SELF"/>
        <data archetype_node_id="at0001">
          <name>
            <value>Event Series</value>
          </name>
          <origin>
            <value>9999-12-10T00:00Z</value>
          </origin>
          <events xsi:type="POINT_EVENT" archetype_node_id="at0002">
            <name>
              <value>Any event</value>
            </name>
            <time>
              <value>9999-12-10T00:00Z</value>
            </time>
            <data xsi:type="ITEM_TREE" archetype_node_id="at0003">
              <name>
                <value>Tree</value>
              </name>
              <items xsi:type="ELEMENT" archetype_node_id="at0005">
                <name>
                  <value>Test name</value>
                </name>
                <value xsi:type="DV_TEXT">
                  <value>KRAS mutation test</value>
                </value>
              </items>
              <items xsi:type="CLUSTER" archetype_node_id="openEHR-EHR-CLUSTER.genetic_variant_presence.v0">
                <name>
                  <value>NRAS exon 4 (codons 117 or 146)</value>
                </name>
                <items xsi:type="ELEMENT" archetype_node_id="at0001">
                  <name>
                    <value>Variant name</value>
                  </name>
                  <value xsi:type="DV_TEXT">
                    <value>NRAS exon 4 (codons 117 or 146)</value>
                  </value>
                </items>
                <items xsi:type="ELEMENT" archetype_node_id="at0002">
                  <name>
                    <value>NRAS exon 4 (codons 117 or 146)</value>
                  </name>
                  <value xsi:type="DV_CODED_TEXT">
                    <value>Indeterminate</value>
                    <defining_code>
                      <terminology_id>
                        <value>local</value>
                      </terminology_id>
                      <code_string>at0007</code_string>
                    </defining_code>
                  </value>
                </items>
              </items>
              <items xsi:type="CLUSTER" archetype_node_id="openEHR-EHR-CLUSTER.genetic_variant_presence.v0">
                <name>
                  <value>NRAS exon 3 (codons 59 or 61)</value>
                </name>
                <items xsi:type="ELEMENT" archetype_node_id="at0001">
                  <name>
                    <value>Variant name</value>
                  </name>
                  <value xsi:type="DV_TEXT">
                    <value>NRAS exon 3 (codons 59 or 61)</value>
                  </value>
                </items>
                <items xsi:type="ELEMENT" archetype_node_id="at0002">
                  <name>
                    <value>NRAS exon 3 (codons 59 or 61)</value>
                  </name>
                  <value xsi:type="DV_CODED_TEXT">
                    <value>Indeterminate</value>
                    <defining_code>
                      <terminology_id>
                        <value>local</value>
                      </terminology_id>
                      <code_string>at0007</code_string>
                    </defining_code>
                  </value>
                </items>
              </items>
              <items xsi:type="CLUSTER" archetype_node_id="openEHR-EHR-CLUSTER.genetic_variant_presence.v0">
                <name>
                  <value>NRAS exon 2 (codons 12 or 13)</value>
                </name>
                <items xsi:type="ELEMENT" archetype_node_id="at0001">
                  <name>
                    <value>Variant name</value>
                  </name>
                  <value xsi:type="DV_TEXT">
                    <value>NRAS exon 2 (codons 12 or 13)</value>
                  </value>
                </items>
                <items xsi:type="ELEMENT" archetype_node_id="at0002">
                  <name>
                    <value>NRAS exon 2 (codons 12 or 13)</value>
                  </name>
                  <value xsi:type="DV_CODED_TEXT">
                    <value>Indeterminate</value>
                    <defining_code>
                      <terminology_id>
                        <value>local</value>
                      </terminology_id>
                      <code_string>at0007</code_string>
                    </defining_code>
                  </value>
                </items>
              </items>
              <items xsi:type="CLUSTER" archetype_node_id="openEHR-EHR-CLUSTER.genetic_variant_presence.v0">
                <name>
                  <value>KRAS exon 4 (codons 117 or 146)</value>
                </name>
                <items xsi:type="ELEMENT" archetype_node_id="at0001">
                  <name>
                    <value>Variant name</value>
                  </name>
                  <value xsi:type="DV_TEXT">
                    <value>KRAS exon 4 (codons 117 or 146)</value>
                  </value>
                </items>
                <items xsi:type="ELEMENT" archetype_node_id="at0002">
                  <name>
                    <value>KRAS exon 4 (codons 117 or 146)</value>
                  </name>
                  <value xsi:type="DV_CODED_TEXT">
                    <value>Indeterminate</value>
                    <defining_code>
                      <terminology_id>
                        <value>local</value>
                      </terminology_id>
                      <code_string>at0007</code_string>
                    </defining_code>
                  </value>
                </items>
              </items>
              <items xsi:type="CLUSTER" archetype_node_id="openEHR-EHR-CLUSTER.genetic_variant_presence.v0">
                <name>
                  <value>KRAS exon 3 (codons 59 or 61)</value>
                </name>
                <items xsi:type="ELEMENT" archetype_node_id="at0001">
                  <name>
                    <value>Variant name</value>
                  </name>
                  <value xsi:type="DV_TEXT">
                    <value>KRAS exon 3 (codons 59 or 61)</value>
                  </value>
                </items>
                <items xsi:type="ELEMENT" archetype_node_id="at0002">
                  <name>
                    <value>KRAS exon 3 (codons 59 or 61)</value>
                  </name>
                  <value xsi:type="DV_CODED_TEXT">
                    <value>Indeterminate</value>
                    <defining_code>
                      <terminology_id>
                        <value>local</value>
                      </terminology_id>
                      <code_string>at0007</code_string>
                    </defining_code>
                  </value>
                </items>
              </items>
              <items xsi:type="CLUSTER" archetype_node_id="openEHR-EHR-CLUSTER.genetic_variant_presence.v0">
                <name>
                  <value>KRAS exon 2 (codons 12 or 13)</value>
                </name>
                <items xsi:type="ELEMENT" archetype_node_id="at0001">
                  <name>
                    <value>Variant name</value>
                  </name>
                  <value xsi:type="DV_TEXT">
                    <value>KRAS exon 2 (codons 12 or 13)</value>
                  </value>
                </items>
                <items xsi:type="ELEMENT" archetype_node_id="at0002">
                  <name>
                    <value>KRAS exon 2 (codons 12 or 13)</value>
                  </name>
                  <value xsi:type="DV_CODED_TEXT">
                    <value>Indeterminate</value>
                    <defining_code>
                      <terminology_id>
                        <value>local</value>
                      </terminology_id>
                      <code_string>at0007</code_string>
                    </defining_code>
                  </value>
                </items>
              </items>
            </data>
          </events>
        </data>
      </items>
      <items xsi:type="OBSERVATION" archetype_node_id="openEHR-EHR-OBSERVATION.laboratory_test_result.v1">
        <name>
          <value>Mismatch repair gene analysis</value>
        </name>
        <archetype_details>
          <archetype_id>
            <value>openEHR-EHR-OBSERVATION.laboratory_test_result.v1</value>
            <qualifiedRmEntity>openEHR-EHR-OBSERVATION</qualifiedRmEntity>
            <domainConcept>laboratory_test_result</domainConcept>
            <rmOriginator>openEHR</rmOriginator>
            <rmName>EHR</rmName>
            <rmEntity>OBSERVATION</rmEntity>
            <versionId>1</versionId>
          </archetype_id>
          <template_id>
            <value>pippo</value>
          </template_id>
          <rm_version>1.0.4</rm_version>
        </archetype_details>
        <language>
          <terminology_id>
            <value>ISO_639-1</value>
          </terminology_id>
          <code_string>en</code_string>
        </language>
        <encoding>
          <terminology_id>
            <value>IANA_character-sets</value>
          </terminology_id>
          <code_string>UTF-8</code_string>
        </encoding>
        <subject xsi:type="PARTY_SELF"/>
        <data archetype_node_id="at0001">
          <name>
            <value>Event Series</value>
          </name>
          <origin>
            <value>9999-12-10T00:00Z</value>
          </origin>
          <events xsi:type="POINT_EVENT" archetype_node_id="at0002">
            <name>
              <value>Any event</value>
            </name>
            <time>
              <value>9999-12-10T00:00Z</value>
            </time>
            <data xsi:type="ITEM_TREE" archetype_node_id="at0003">
              <name>
                <value>Tree</value>
              </name>
              <items xsi:type="ELEMENT" archetype_node_id="at0005">
                <name>
                  <value>Test name</value>
                </name>
                <value xsi:type="DV_TEXT">
                  <value>Mismatch repair gene expression</value>
                </value>
              </items>
              <items xsi:type="ELEMENT" archetype_node_id="at0057">
                <name>
                  <value>Mismatch repair gene expression</value>
                </name>
                <value xsi:type="DV_TEXT">
                  <value>Not done</value>
                </value>
              </items>
            </data>
          </events>
        </data>
      </items>
    </items>
  </content>
  <content xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:type="SECTION" archetype_node_id="openEHR-EHR-SECTION.demographics_rcp.v1">
    <name>
      <value>Patient data</value>
    </name>
    <items xsi:type="EVALUATION" archetype_node_id="openEHR-EHR-EVALUATION.gender.v1">
      <name>
        <value>Gender</value>
      </name>
      <archetype_details>
        <archetype_id>
          <value>openEHR-EHR-EVALUATION.gender.v1</value>
          <qualifiedRmEntity>openEHR-EHR-EVALUATION</qualifiedRmEntity>
          <domainConcept>gender</domainConcept>
          <rmOriginator>openEHR</rmOriginator>
          <rmName>EHR</rmName>
          <rmEntity>EVALUATION</rmEntity>
          <versionId>1</versionId>
        </archetype_id>
        <template_id>
          <value>pippo</value>
        </template_id>
        <rm_version>1.0.4</rm_version>
      </archetype_details>
      <language>
        <terminology_id>
          <value>ISO_639-1</value>
        </terminology_id>
        <code_string>en</code_string>
      </language>
      <encoding>
        <terminology_id>
          <value>IANA_character-sets</value>
        </terminology_id>
        <code_string>UTF-8</code_string>
      </encoding>
      <subject xsi:type="PARTY_SELF"/>
      <data xsi:type="ITEM_TREE" archetype_node_id="at0002">
        <name>
          <value>Tree</value>
        </name>
        <items xsi:type="ELEMENT" archetype_node_id="at0019">
          <name>
            <value>Biological sex</value>
          </name>
          <value xsi:type="DV_CODED_TEXT">
            <value>FEMALE</value>
            <defining_code>
              <terminology_id>
                <value>omop_vocabulary</value>
              </terminology_id>
              <code_string>8532</code_string>
            </defining_code>
          </value>
        </items>
      </data>
    </items>
    <items xsi:type="EVALUATION" archetype_node_id="openEHR-EHR-EVALUATION.problem_diagnosis.v1">
      <name>
        <value>Primary diagnosis</value>
      </name>
      <archetype_details>
        <archetype_id>
          <value>openEHR-EHR-EVALUATION.problem_diagnosis.v1</value>
          <qualifiedRmEntity>openEHR-EHR-EVALUATION</qualifiedRmEntity>
          <domainConcept>problem_diagnosis</domainConcept>
          <rmOriginator>openEHR</rmOriginator>
          <rmName>EHR</rmName>
          <rmEntity>EVALUATION</rmEntity>
          <versionId>1</versionId>
        </archetype_id>
        <template_id>
          <value>pippo</value>
        </template_id>
        <rm_version>1.0.4</rm_version>
      </archetype_details>
      <language>
        <terminology_id>
          <value>ISO_639-1</value>
        </terminology_id>
        <code_string>en</code_string>
      </language>
      <encoding>
        <terminology_id>
          <value>IANA_character-sets</value>
        </terminology_id>
        <code_string>UTF-8</code_string>
      </encoding>
      <subject xsi:type="PARTY_SELF"/>
      <data xsi:type="ITEM_TREE" archetype_node_id="at0001">
        <name>
          <value>structure</value>
        </name>
        <items xsi:type="ELEMENT" archetype_node_id="at0002">
          <name>
            <value>Primary diagnosis</value>
          </name>
          <value xsi:type="DV_CODED_TEXT">
            <value>Colorectal cancer</value>
            <defining_code>
              <terminology_id>
                <value>omop_vocabulary</value>
              </terminology_id>
              <code_string>44803809</code_string>
            </defining_code>
          </value>
        </items>
        <items xsi:type="ELEMENT" archetype_node_id="at0003">
          <name>
            <value>Date of diagnosis</value>
          </name>
          <value xsi:type="DV_DATE_TIME">
            <value>2022-03-01T00:00Z</value>
          </value>
        </items>
        <items xsi:type="CLUSTER" archetype_node_id="openEHR-EHR-CLUSTER.timing_nondaily.v1">
          <name>
            <value>Diagnosis timing</value>
          </name>
          <items xsi:type="CLUSTER" archetype_node_id="at0006">
            <name>
              <value>Primary diagnosis</value>
            </name>
            <items xsi:type="ELEMENT" archetype_node_id="at0009">
              <name>
                <value>Age at diagnosis</value>
              </name>
              <value xsi:type="DV_DURATION">
                <value>P55Y</value>
              </value>
            </items>
          </items>
        </items>
      </data>
    </items>
    <items xsi:type="EVALUATION" archetype_node_id="openEHR-EHR-EVALUATION.problem_diagnosis.v1">
      <name>
        <value>Metastasis diagnosis</value>
      </name>
      <archetype_details>
        <archetype_id>
          <value>openEHR-EHR-EVALUATION.problem_diagnosis.v1</value>
          <qualifiedRmEntity>openEHR-EHR-EVALUATION</qualifiedRmEntity>
          <domainConcept>problem_diagnosis</domainConcept>
          <rmOriginator>openEHR</rmOriginator>
          <rmName>EHR</rmName>
          <rmEntity>EVALUATION</rmEntity>
          <versionId>1</versionId>
        </archetype_id>
        <template_id>
          <value>pippo</value>
        </template_id>
        <rm_version>1.0.4</rm_version>
      </archetype_details>
      <language>
        <terminology_id>
          <value>ISO_639-1</value>
        </terminology_id>
        <code_string>en</code_string>
      </language>
      <encoding>
        <terminology_id>
          <value>IANA_character-sets</value>
        </terminology_id>
        <code_string>UTF-8</code_string>
      </encoding>
      <subject xsi:type="PARTY_SELF"/>
      <data xsi:type="ITEM_TREE" archetype_node_id="at0001">
        <name>
          <value>structure</value>
        </name>
        <items xsi:type="ELEMENT" archetype_node_id="at0002">
          <name>
            <value>Metastasis diagnosis</value>
          </name>
          <value xsi:type="DV_CODED_TEXT">
            <value>Metastasis</value>
            <defining_code>
              <terminology_id>
                <value>omop_vocabulary</value>
              </terminology_id>
              <code_string>36769180</code_string>
            </defining_code>
          </value>
        </items>
        <items xsi:type="CLUSTER" archetype_node_id="openEHR-EHR-CLUSTER.timing_nondaily.v1">
          <name>
            <value>Metastasis diagnosis</value>
          </name>
          <items xsi:type="CLUSTER" archetype_node_id="at0006">
            <name>
              <value>Metastasis diagnosis</value>
            </name>
            <items xsi:type="ELEMENT" archetype_node_id="at0005">
              <name>
                <value>From event</value>
              </name>
              <value xsi:type="DV_TEXT">
                <value>Primary diagnosis</value>
              </value>
            </items>
            <items xsi:type="ELEMENT" archetype_node_id="at0009">
              <name>
                <value>Time of recurrence</value>
              </name>
              <value xsi:type="DV_DURATION">
                <value>P112W</value>
              </value>
            </items>
          </items>
        </items>
      </data>
    </items>
  </content>
</composition>
    '''
    xml2='''<composition xmlns:ns2="http://schemas.openehr.org/v1" archetype_node_id="openEHR-EHR-COMPOSITION.report.v1">
  <name>
    <value>pippo</value>
  </name>
  <uid xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:type="OBJECT_VERSION_ID">
    <value>0c770609-2ded-4c0f-aa7b-9b9352f6c90c::local.ehrbase.org::1</value>
  </uid>
  <archetype_details>
    <archetype_id>
      <value>openEHR-EHR-COMPOSITION.report.v1</value>
      <qualifiedRmEntity>openEHR-EHR-COMPOSITION</qualifiedRmEntity>
      <domainConcept>report</domainConcept>
      <rmOriginator>openEHR</rmOriginator>
      <rmName>EHR</rmName>
      <rmEntity>COMPOSITION</rmEntity>
      <versionId>1</versionId>
    </archetype_id>
    <template_id>
      <value>pippo</value>
    </template_id>
    <rm_version>1.0.4</rm_version>
  </archetype_details>
  <language>
    <terminology_id>
      <value>ISO_639-1</value>
    </terminology_id>
    <code_string>en</code_string>
  </language>
  <territory>
    <terminology_id>
      <value>ISO_3166-1</value>
    </terminology_id>
    <code_string>ZW</code_string>
  </territory>
  <category>
    <value>event</value>
    <defining_code>
      <terminology_id>
        <value>openehr</value>
      </terminology_id>
      <code_string>433</code_string>
    </defining_code>
  </category>
  <composer xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:type="PARTY_IDENTIFIED">
    <name>EOSC-Life_WP1-DEM</name>
  </composer>
  <context>
    <start_time>
      <value>2022-03-15T12:04:38.490Z</value>
    </start_time>
    <setting>
      <value>other care</value>
      <defining_code>
        <terminology_id>
          <value>openehr</value>
        </terminology_id>
        <code_string>238</code_string>
      </defining_code>
    </setting>
    <other_context xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:type="ITEM_TREE" archetype_node_id="at0001">
      <name>
        <value>Tree</value>
      </name>
      <items xsi:type="CLUSTER" archetype_node_id="openEHR-EHR-CLUSTER.case_identification.v0">
        <name>
          <value>Case identification</value>
        </name>
        <items xsi:type="ELEMENT" archetype_node_id="at0001">
          <name>
            <value>Patient pseudonym</value>
          </name>
          <value xsi:type="DV_TEXT">
            <value>1749123</value>
          </value>
        </items>
        <items xsi:type="ELEMENT" archetype_node_id="at0006">
          <name>
            <value>Participation in clinical study</value>
          </name>
          <value xsi:type="DV_TEXT">
            <value>FALSE</value>
          </value>
        </items>
      </items>
    </other_context>
  </context>
  <content xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:type="SECTION" archetype_node_id="openEHR-EHR-SECTION.adhoc.v1">
    <name>
      <value>Sample</value>
    </name>
    <items xsi:type="EVALUATION" archetype_node_id="openEHR-EHR-EVALUATION.biospecimen_summary.v0">
      <name>
        <value>Biospecimen summary</value>
      </name>
      <archetype_details>
        <archetype_id>
          <value>openEHR-EHR-EVALUATION.biospecimen_summary.v0</value>
          <qualifiedRmEntity>openEHR-EHR-EVALUATION</qualifiedRmEntity>
          <domainConcept>biospecimen_summary</domainConcept>
          <rmOriginator>openEHR</rmOriginator>
          <rmName>EHR</rmName>
          <rmEntity>EVALUATION</rmEntity>
          <versionId>0</versionId>
        </archetype_id>
        <template_id>
          <value>pippo</value>
        </template_id>
        <rm_version>1.0.4</rm_version>
      </archetype_details>
      <language>
        <terminology_id>
          <value>ISO_639-1</value>
        </terminology_id>
        <code_string>en</code_string>
      </language>
      <encoding>
        <terminology_id>
          <value>IANA_character-sets</value>
        </terminology_id>
        <code_string>UTF-8</code_string>
      </encoding>
      <subject xsi:type="PARTY_SELF"/>
      <data xsi:type="ITEM_TREE" archetype_node_id="at0001">
        <name>
          <value>Item tree</value>
        </name>
        <items xsi:type="ELEMENT" archetype_node_id="at0002">
          <name>
            <value>Sample ID</value>
          </name>
          <value xsi:type="DV_IDENTIFIER">
            <issuer>unknown</issuer>
            <assigner>unknown</assigner>
            <id>557</id>
            <type>unknown</type>
          </value>
        </items>
        <items xsi:type="ELEMENT" archetype_node_id="at0003">
          <name>
            <value>Material type</value>
          </name>
          <value xsi:type="DV_CODED_TEXT">
            <value>Tumor tissue sample</value>
            <defining_code>
              <terminology_id>
                <value>omop_vocabulary</value>
              </terminology_id>
              <code_string>4122248</code_string>
            </defining_code>
          </value>
        </items>
        <items xsi:type="ELEMENT" archetype_node_id="at0007">
          <name>
            <value>Preservation mode</value>
          </name>
          <value xsi:type="DV_CODED_TEXT">
            <value>FFPE</value>
            <defining_code>
              <terminology_id>
                <value>omop_vocabulary</value>
              </terminology_id>
              <code_string>37206850</code_string>
            </defining_code>
          </value>
        </items>
        <items xsi:type="CLUSTER" archetype_node_id="openEHR-EHR-CLUSTER.specimen.v1">
          <name>
            <value>Specimen</value>
          </name>
          <items xsi:type="ELEMENT" archetype_node_id="at0015">
            <name>
              <value>Year of sample collection</value>
            </name>
            <value xsi:type="DV_DATE_TIME">
              <value>2022-01-01T00:00Z</value>
            </value>
          </items>
        </items>
      </data>
    </items>
  </content>
  <content xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:type="SECTION" archetype_node_id="openEHR-EHR-SECTION.adhoc.v1">
    <name>
      <value>Surgery</value>
    </name>
    <items xsi:type="ACTION" archetype_node_id="openEHR-EHR-ACTION.procedure.v1">
      <name>
        <value>Surgery</value>
      </name>
      <archetype_details>
        <archetype_id>
          <value>openEHR-EHR-ACTION.procedure.v1</value>
          <qualifiedRmEntity>openEHR-EHR-ACTION</qualifiedRmEntity>
          <domainConcept>procedure</domainConcept>
          <rmOriginator>openEHR</rmOriginator>
          <rmName>EHR</rmName>
          <rmEntity>ACTION</rmEntity>
          <versionId>1</versionId>
        </archetype_id>
        <template_id>
          <value>pippo</value>
        </template_id>
        <rm_version>1.0.4</rm_version>
      </archetype_details>
      <language>
        <terminology_id>
          <value>ISO_639-1</value>
        </terminology_id>
        <code_string>en</code_string>
      </language>
      <encoding>
        <terminology_id>
          <value>IANA_character-sets</value>
        </terminology_id>
        <code_string>UTF-8</code_string>
      </encoding>
      <subject xsi:type="PARTY_SELF"/>
      <time>
        <value>2018-11-07T00:00Z</value>
      </time>
      <description xsi:type="ITEM_TREE" archetype_node_id="at0001">
        <name>
          <value>Tree</value>
        </name>
        <items xsi:type="ELEMENT" archetype_node_id="at0002">
          <name>
            <value>Surgery type</value>
          </name>
          <value xsi:type="DV_CODED_TEXT">
            <value>Anterior resection of rectum</value>
            <defining_code>
              <terminology_id>
                <value>omop_vocabulary</value>
              </terminology_id>
              <code_string>4166855</code_string>
            </defining_code>
          </value>
        </items>
        <items xsi:type="ELEMENT" archetype_node_id="at0048">
          <name>
            <value>Surgery radicality</value>
          </name>
          <value xsi:type="DV_CODED_TEXT">
            <value>R2</value>
            <defining_code>
              <terminology_id>
                <value>omop_vocabulary</value>
              </terminology_id>
              <code_string>4121182</code_string>
            </defining_code>
          </value>
        </items>
        <items xsi:type="ELEMENT" archetype_node_id="at0063">
          <name>
            <value>Location of the tumor</value>
          </name>
          <value xsi:type="DV_CODED_TEXT">
            <value>C 20 - Rectum</value>
            <defining_code>
              <terminology_id>
                <value>omop_vocabulary</value>
              </terminology_id>
              <code_string>74582</code_string>
            </defining_code>
          </value>
        </items>
        <items xsi:type="CLUSTER" archetype_node_id="openEHR-EHR-CLUSTER.timing_nondaily.v1">
          <name>
            <value>Surgery timing</value>
          </name>
          <items xsi:type="CLUSTER" archetype_node_id="at0006">
            <name>
              <value>Surgery</value>
            </name>
            <items xsi:type="ELEMENT" archetype_node_id="at0005">
              <name>
                <value>From event</value>
              </name>
              <value xsi:type="DV_TEXT">
                <value>Primary diagnosis</value>
              </value>
            </items>
            <items xsi:type="ELEMENT" archetype_node_id="at0009">
              <name>
                <value>Surgery start relative</value>
              </name>
              <value xsi:type="DV_DURATION">
                <value>P7D</value>
              </value>
            </items>
          </items>
        </items>
      </description>
      <ism_transition>
        <current_state>
          <value>completed</value>
          <defining_code>
            <terminology_id>
              <value>openehr</value>
            </terminology_id>
            <code_string>532</code_string>
          </defining_code>
        </current_state>
      </ism_transition>
    </items>
  </content>
  <content xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:type="SECTION" archetype_node_id="openEHR-EHR-SECTION.adhoc.v1">
    <name>
      <value>Diagnostic examinations</value>
    </name>
    <items xsi:type="ACTION" archetype_node_id="openEHR-EHR-ACTION.procedure.v1">
      <name>
        <value>Colonoscopy</value>
      </name>
      <archetype_details>
        <archetype_id>
          <value>openEHR-EHR-ACTION.procedure.v1</value>
          <qualifiedRmEntity>openEHR-EHR-ACTION</qualifiedRmEntity>
          <domainConcept>procedure</domainConcept>
          <rmOriginator>openEHR</rmOriginator>
          <rmName>EHR</rmName>
          <rmEntity>ACTION</rmEntity>
          <versionId>1</versionId>
        </archetype_id>
        <template_id>
          <value>pippo</value>
        </template_id>
        <rm_version>1.0.4</rm_version>
      </archetype_details>
      <language>
        <terminology_id>
          <value>ISO_639-1</value>
        </terminology_id>
        <code_string>en</code_string>
      </language>
      <encoding>
        <terminology_id>
          <value>IANA_character-sets</value>
        </terminology_id>
        <code_string>UTF-8</code_string>
      </encoding>
      <subject xsi:type="PARTY_SELF"/>
      <time>
        <value>9999-12-10T00:00Z</value>
      </time>
      <description xsi:type="ITEM_TREE" archetype_node_id="at0001">
        <name>
          <value>Tree</value>
        </name>
        <items xsi:type="ELEMENT" archetype_node_id="at0002">
          <name>
            <value>Procedure name</value>
          </name>
          <value xsi:type="DV_TEXT">
            <value>Colonoscopy</value>
          </value>
        </items>
        <items xsi:type="ELEMENT" archetype_node_id="at0048">
          <name>
            <value>Colonoscopy</value>
          </name>
          <value xsi:type="DV_TEXT">
            <value>Not done</value>
          </value>
        </items>
      </description>
      <ism_transition>
        <current_state>
          <value>completed</value>
          <defining_code>
            <terminology_id>
              <value>openehr</value>
            </terminology_id>
            <code_string>532</code_string>
          </defining_code>
        </current_state>
      </ism_transition>
    </items>
    <items xsi:type="ACTION" archetype_node_id="openEHR-EHR-ACTION.procedure.v1">
      <name>
        <value>CT</value>
      </name>
      <archetype_details>
        <archetype_id>
          <value>openEHR-EHR-ACTION.procedure.v1</value>
          <qualifiedRmEntity>openEHR-EHR-ACTION</qualifiedRmEntity>
          <domainConcept>procedure</domainConcept>
          <rmOriginator>openEHR</rmOriginator>
          <rmName>EHR</rmName>
          <rmEntity>ACTION</rmEntity>
          <versionId>1</versionId>
        </archetype_id>
        <template_id>
          <value>pippo</value>
        </template_id>
        <rm_version>1.0.4</rm_version>
      </archetype_details>
      <language>
        <terminology_id>
          <value>ISO_639-1</value>
        </terminology_id>
        <code_string>en</code_string>
      </language>
      <encoding>
        <terminology_id>
          <value>IANA_character-sets</value>
        </terminology_id>
        <code_string>UTF-8</code_string>
      </encoding>
      <subject xsi:type="PARTY_SELF"/>
      <time>
        <value>9999-12-10T00:00Z</value>
      </time>
      <description xsi:type="ITEM_TREE" archetype_node_id="at0001">
        <name>
          <value>Tree</value>
        </name>
        <items xsi:type="ELEMENT" archetype_node_id="at0002">
          <name>
            <value>Procedure name</value>
          </name>
          <value xsi:type="DV_TEXT">
            <value>CT</value>
          </value>
        </items>
        <items xsi:type="ELEMENT" archetype_node_id="at0048">
          <name>
            <value>CT</value>
          </name>
          <value xsi:type="DV_TEXT">
            <value>Done, data available</value>
          </value>
        </items>
      </description>
      <ism_transition>
        <current_state>
          <value>completed</value>
          <defining_code>
            <terminology_id>
              <value>openehr</value>
            </terminology_id>
            <code_string>532</code_string>
          </defining_code>
        </current_state>
      </ism_transition>
    </items>
    <items xsi:type="ACTION" archetype_node_id="openEHR-EHR-ACTION.procedure.v1">
      <name>
        <value>Liver imaging</value>
      </name>
      <archetype_details>
        <archetype_id>
          <value>openEHR-EHR-ACTION.procedure.v1</value>
          <qualifiedRmEntity>openEHR-EHR-ACTION</qualifiedRmEntity>
          <domainConcept>procedure</domainConcept>
          <rmOriginator>openEHR</rmOriginator>
          <rmName>EHR</rmName>
          <rmEntity>ACTION</rmEntity>
          <versionId>1</versionId>
        </archetype_id>
        <template_id>
          <value>pippo</value>
        </template_id>
        <rm_version>1.0.4</rm_version>
      </archetype_details>
      <language>
        <terminology_id>
          <value>ISO_639-1</value>
        </terminology_id>
        <code_string>en</code_string>
      </language>
      <encoding>
        <terminology_id>
          <value>IANA_character-sets</value>
        </terminology_id>
        <code_string>UTF-8</code_string>
      </encoding>
      <subject xsi:type="PARTY_SELF"/>
      <time>
        <value>9999-12-10T00:00Z</value>
      </time>
      <description xsi:type="ITEM_TREE" archetype_node_id="at0001">
        <name>
          <value>Tree</value>
        </name>
        <items xsi:type="ELEMENT" archetype_node_id="at0002">
          <name>
            <value>Procedure name</value>
          </name>
          <value xsi:type="DV_TEXT">
            <value>Liver imaging</value>
          </value>
        </items>
        <items xsi:type="ELEMENT" archetype_node_id="at0048">
          <name>
            <value>Liver imaging</value>
          </name>
          <value xsi:type="DV_TEXT">
            <value>Done, data available</value>
          </value>
        </items>
      </description>
      <ism_transition>
        <current_state>
          <value>completed</value>
          <defining_code>
            <terminology_id>
              <value>openehr</value>
            </terminology_id>
            <code_string>532</code_string>
          </defining_code>
        </current_state>
      </ism_transition>
    </items>
    <items xsi:type="ACTION" archetype_node_id="openEHR-EHR-ACTION.procedure.v1">
      <name>
        <value>Lung imaging</value>
      </name>
      <archetype_details>
        <archetype_id>
          <value>openEHR-EHR-ACTION.procedure.v1</value>
          <qualifiedRmEntity>openEHR-EHR-ACTION</qualifiedRmEntity>
          <domainConcept>procedure</domainConcept>
          <rmOriginator>openEHR</rmOriginator>
          <rmName>EHR</rmName>
          <rmEntity>ACTION</rmEntity>
          <versionId>1</versionId>
        </archetype_id>
        <template_id>
          <value>pippo</value>
        </template_id>
        <rm_version>1.0.4</rm_version>
      </archetype_details>
      <language>
        <terminology_id>
          <value>ISO_639-1</value>
        </terminology_id>
        <code_string>en</code_string>
      </language>
      <encoding>
        <terminology_id>
          <value>IANA_character-sets</value>
        </terminology_id>
        <code_string>UTF-8</code_string>
      </encoding>
      <subject xsi:type="PARTY_SELF"/>
      <time>
        <value>9999-12-10T00:00Z</value>
      </time>
      <description xsi:type="ITEM_TREE" archetype_node_id="at0001">
        <name>
          <value>Tree</value>
        </name>
        <items xsi:type="ELEMENT" archetype_node_id="at0002">
          <name>
            <value>Procedure name</value>
          </name>
          <value xsi:type="DV_TEXT">
            <value>Lung imaging</value>
          </value>
        </items>
        <items xsi:type="ELEMENT" archetype_node_id="at0048">
          <name>
            <value>Lung imaging</value>
          </name>
          <value xsi:type="DV_TEXT">
            <value>Done, data available</value>
          </value>
        </items>
      </description>
      <ism_transition>
        <current_state>
          <value>completed</value>
          <defining_code>
            <terminology_id>
              <value>openehr</value>
            </terminology_id>
            <code_string>532</code_string>
          </defining_code>
        </current_state>
      </ism_transition>
    </items>
    <items xsi:type="ACTION" archetype_node_id="openEHR-EHR-ACTION.procedure.v1">
      <name>
        <value>MRI</value>
      </name>
      <archetype_details>
        <archetype_id>
          <value>openEHR-EHR-ACTION.procedure.v1</value>
          <qualifiedRmEntity>openEHR-EHR-ACTION</qualifiedRmEntity>
          <domainConcept>procedure</domainConcept>
          <rmOriginator>openEHR</rmOriginator>
          <rmName>EHR</rmName>
          <rmEntity>ACTION</rmEntity>
          <versionId>1</versionId>
        </archetype_id>
        <template_id>
          <value>pippo</value>
        </template_id>
        <rm_version>1.0.4</rm_version>
      </archetype_details>
      <language>
        <terminology_id>
          <value>ISO_639-1</value>
        </terminology_id>
        <code_string>en</code_string>
      </language>
      <encoding>
        <terminology_id>
          <value>IANA_character-sets</value>
        </terminology_id>
        <code_string>UTF-8</code_string>
      </encoding>
      <subject xsi:type="PARTY_SELF"/>
      <time>
        <value>9999-12-10T00:00Z</value>
      </time>
      <description xsi:type="ITEM_TREE" archetype_node_id="at0001">
        <name>
          <value>Tree</value>
        </name>
        <items xsi:type="ELEMENT" archetype_node_id="at0002">
          <name>
            <value>Procedure name</value>
          </name>
          <value xsi:type="DV_TEXT">
            <value>MRI</value>
          </value>
        </items>
        <items xsi:type="ELEMENT" archetype_node_id="at0048">
          <name>
            <value>MRI</value>
          </name>
          <value xsi:type="DV_TEXT">
            <value>Unknown</value>
          </value>
        </items>
      </description>
      <ism_transition>
        <current_state>
          <value>completed</value>
          <defining_code>
            <terminology_id>
              <value>openehr</value>
            </terminology_id>
            <code_string>532</code_string>
          </defining_code>
        </current_state>
      </ism_transition>
    </items>
  </content>
  <content xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:type="SECTION" archetype_node_id="openEHR-EHR-SECTION.adhoc.v1">
    <name>
      <value>Vital status and survival information</value>
    </name>
    <items xsi:type="EVALUATION" archetype_node_id="openEHR-EHR-EVALUATION.clinical_synopsis.v1">
      <name>
        <value>Vital status and survival information</value>
      </name>
      <archetype_details>
        <archetype_id>
          <value>openEHR-EHR-EVALUATION.clinical_synopsis.v1</value>
          <qualifiedRmEntity>openEHR-EHR-EVALUATION</qualifiedRmEntity>
          <domainConcept>clinical_synopsis</domainConcept>
          <rmOriginator>openEHR</rmOriginator>
          <rmName>EHR</rmName>
          <rmEntity>EVALUATION</rmEntity>
          <versionId>1</versionId>
        </archetype_id>
        <template_id>
          <value>pippo</value>
        </template_id>
        <rm_version>1.0.4</rm_version>
      </archetype_details>
      <language>
        <terminology_id>
          <value>ISO_639-1</value>
        </terminology_id>
        <code_string>en</code_string>
      </language>
      <encoding>
        <terminology_id>
          <value>IANA_character-sets</value>
        </terminology_id>
        <code_string>UTF-8</code_string>
      </encoding>
      <subject xsi:type="PARTY_SELF"/>
      <protocol xsi:type="ITEM_TREE" archetype_node_id="at0003">
        <name>
          <value>Tree</value>
        </name>
        <items xsi:type="CLUSTER" archetype_node_id="openEHR-EHR-CLUSTER.timing_nondaily.v1">
          <name>
            <value>Vital status timing</value>
          </name>
          <items xsi:type="ELEMENT" archetype_node_id="at0001">
            <name>
              <value>Timestamp of last update of vital status</value>
            </name>
            <value xsi:type="DV_DATE">
              <value>2002-04-01</value>
            </value>
          </items>
          <items xsi:type="CLUSTER" archetype_node_id="at0006">
            <name>
              <value>Overall survival status</value>
            </name>
            <items xsi:type="ELEMENT" archetype_node_id="at0005">
              <name>
                <value>From event</value>
              </name>
              <value xsi:type="DV_TEXT">
                <value>First colon cancer therapy</value>
              </value>
            </items>
            <items xsi:type="ELEMENT" archetype_node_id="at0009">
              <name>
                <value>Overall survival status</value>
              </name>
              <value xsi:type="DV_DURATION">
                <value>P455D</value>
              </value>
            </items>
          </items>
        </items>
      </protocol>
      <data xsi:type="ITEM_TREE" archetype_node_id="at0001">
        <name>
          <value>List</value>
        </name>
        <items xsi:type="ELEMENT" archetype_node_id="at0002">
          <name>
            <value>Vital status</value>
          </name>
          <value xsi:type="DV_TEXT">
            <value>death for unknown reasons</value>
          </value>
        </items>
      </data>
    </items>
  </content>
  <content xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:type="SECTION" archetype_node_id="openEHR-EHR-SECTION.result_details.v0">
    <name>
      <value>Histopathology</value>
    </name>
    <items xsi:type="SECTION" archetype_node_id="at0002">
      <name>
        <value>Result group</value>
      </name>
      <items xsi:type="EVALUATION" archetype_node_id="openEHR-EHR-EVALUATION.problem_diagnosis.v1">
        <name>
          <value>Cancer diagnosis</value>
        </name>
        <archetype_details>
          <archetype_id>
            <value>openEHR-EHR-EVALUATION.problem_diagnosis.v1</value>
            <qualifiedRmEntity>openEHR-EHR-EVALUATION</qualifiedRmEntity>
            <domainConcept>problem_diagnosis</domainConcept>
            <rmOriginator>openEHR</rmOriginator>
            <rmName>EHR</rmName>
            <rmEntity>EVALUATION</rmEntity>
            <versionId>1</versionId>
          </archetype_id>
          <template_id>
            <value>pippo</value>
          </template_id>
          <rm_version>1.0.4</rm_version>
        </archetype_details>
        <language>
          <terminology_id>
            <value>ISO_639-1</value>
          </terminology_id>
          <code_string>en</code_string>
        </language>
        <encoding>
          <terminology_id>
            <value>IANA_character-sets</value>
          </terminology_id>
          <code_string>UTF-8</code_string>
        </encoding>
        <subject xsi:type="PARTY_SELF"/>
        <data xsi:type="ITEM_TREE" archetype_node_id="at0001">
          <name>
            <value>structure</value>
          </name>
          <items xsi:type="ELEMENT" archetype_node_id="at0002">
            <name>
              <value>Problem/Diagnosis name</value>
            </name>
            <value xsi:type="DV_CODED_TEXT">
              <value>Colorectal cancer</value>
              <defining_code>
                <terminology_id>
                  <value>omop_vocabulary</value>
                </terminology_id>
                <code_string>44803809</code_string>
              </defining_code>
            </value>
          </items>
          <items xsi:type="ELEMENT" archetype_node_id="at0012">
            <name>
              <value>Localization of primary tumor</value>
            </name>
            <value xsi:type="DV_CODED_TEXT">
              <value>C 20 - Rectum</value>
              <defining_code>
                <terminology_id>
                  <value>omop_vocabulary</value>
                </terminology_id>
                <code_string>74582</code_string>
              </defining_code>
            </value>
          </items>
          <items xsi:type="CLUSTER" archetype_node_id="openEHR-EHR-CLUSTER.synoptic_details_colorectal_carcinoma.v0">
            <name>
              <value>Synoptic details - Colorectal cancer</value>
            </name>
            <items xsi:type="CLUSTER" archetype_node_id="at0001">
              <name>
                <value>Microscopic findings</value>
              </name>
              <items xsi:type="ELEMENT" archetype_node_id="at0033">
                <name>
                  <value>Morphology</value>
                </name>
                <value xsi:type="DV_CODED_TEXT">
                  <value>Adenocarcinoma</value>
                  <defining_code>
                    <terminology_id>
                      <value>omop_vocabulary</value>
                    </terminology_id>
                    <code_string>42530737</code_string>
                  </defining_code>
                </value>
              </items>
              <items xsi:type="CLUSTER" archetype_node_id="at0263">
                <name>
                  <value>Distant metastasis</value>
                </name>
                <items xsi:type="CLUSTER" archetype_node_id="openEHR-EHR-CLUSTER.anatomical_location.v1">
                  <name>
                    <value>Anatomical location</value>
                  </name>
                  <items xsi:type="ELEMENT" archetype_node_id="at0001">
                    <name>
                      <value>Localization of metastasis</value>
                    </name>
                    <value xsi:type="DV_CODED_TEXT">
                      <value>Lymph Nodes</value>
                      <defining_code>
                        <terminology_id>
                          <value>omop_vocabulary</value>
                        </terminology_id>
                        <code_string>45881859</code_string>
                      </defining_code>
                    </value>
                  </items>
                </items>
              </items>
              <items xsi:type="CLUSTER" archetype_node_id="at0269">
                <name>
                  <value>Histological grading</value>
                </name>
                <items xsi:type="ELEMENT" archetype_node_id="at0271">
                  <name>
                    <value>WHO version</value>
                  </name>
                  <value xsi:type="DV_TEXT">
                    <value>2nd ed. (1991- 2000)</value>
                  </value>
                </items>
              </items>
              <items xsi:type="CLUSTER" archetype_node_id="openEHR-EHR-CLUSTER.tnm-pathological.v1">
                <name>
                  <value>TNM pathological classification</value>
                </name>
                <items xsi:type="ELEMENT" archetype_node_id="at0006">
                  <name>
                    <value>Grade</value>
                  </name>
                  <value xsi:type="DV_CODED_TEXT">
                    <value>G3</value>
                    <defining_code>
                      <terminology_id>
                        <value>omop_vocabulary</value>
                      </terminology_id>
                      <code_string>36769033</code_string>
                    </defining_code>
                  </value>
                </items>
                <items xsi:type="ELEMENT" archetype_node_id="at0032">
                  <name>
                    <value>UICC version</value>
                  </name>
                  <value xsi:type="DV_TEXT">
                    <value>5th. ed (used 1998-2002)</value>
                  </value>
                </items>
                <items xsi:type="ELEMENT" archetype_node_id="at0003.1">
                  <name>
                    <value>Primary tumour</value>
                  </name>
                  <value xsi:type="DV_CODED_TEXT">
                    <value>T3</value>
                    <defining_code>
                      <terminology_id>
                        <value>omop_vocabulary</value>
                      </terminology_id>
                      <code_string>4234703</code_string>
                    </defining_code>
                  </value>
                </items>
                <items xsi:type="ELEMENT" archetype_node_id="at0004.1">
                  <name>
                    <value>Regional lymph nodes</value>
                  </name>
                  <value xsi:type="DV_CODED_TEXT">
                    <value>N2</value>
                    <defining_code>
                      <terminology_id>
                        <value>omop_vocabulary</value>
                      </terminology_id>
                      <code_string>45881614</code_string>
                    </defining_code>
                  </value>
                </items>
                <items xsi:type="ELEMENT" archetype_node_id="at0005.1">
                  <name>
                    <value>Distant metastasis</value>
                  </name>
                  <value xsi:type="DV_CODED_TEXT">
                    <value>MX</value>
                    <defining_code>
                      <terminology_id>
                        <value>omop_vocabulary</value>
                      </terminology_id>
                      <code_string>45876323</code_string>
                    </defining_code>
                  </value>
                </items>
                <items xsi:type="ELEMENT" archetype_node_id="at0031.1">
                  <name>
                    <value>Stage</value>
                  </name>
                  <value xsi:type="DV_CODED_TEXT">
                    <value>Stage - III</value>
                    <defining_code>
                      <terminology_id>
                        <value>omop_vocabulary</value>
                      </terminology_id>
                      <code_string>45878643</code_string>
                    </defining_code>
                  </value>
                </items>
              </items>
            </items>
          </items>
        </data>
      </items>
      <items xsi:type="OBSERVATION" archetype_node_id="openEHR-EHR-OBSERVATION.laboratory_test_result.v1">
        <name>
          <value>Laboratory test result</value>
        </name>
        <archetype_details>
          <archetype_id>
            <value>openEHR-EHR-OBSERVATION.laboratory_test_result.v1</value>
            <qualifiedRmEntity>openEHR-EHR-OBSERVATION</qualifiedRmEntity>
            <domainConcept>laboratory_test_result</domainConcept>
            <rmOriginator>openEHR</rmOriginator>
            <rmName>EHR</rmName>
            <rmEntity>OBSERVATION</rmEntity>
            <versionId>1</versionId>
          </archetype_id>
          <template_id>
            <value>pippo</value>
          </template_id>
          <rm_version>1.0.4</rm_version>
        </archetype_details>
        <language>
          <terminology_id>
            <value>ISO_639-1</value>
          </terminology_id>
          <code_string>en</code_string>
        </language>
        <encoding>
          <terminology_id>
            <value>IANA_character-sets</value>
          </terminology_id>
          <code_string>UTF-8</code_string>
        </encoding>
        <subject xsi:type="PARTY_SELF"/>
        <data archetype_node_id="at0001">
          <name>
            <value>Event Series</value>
          </name>
          <origin>
            <value>2018-11-07T00:00Z</value>
          </origin>
          <events xsi:type="POINT_EVENT" archetype_node_id="at0002">
            <name>
              <value>Any event</value>
            </name>
            <time>
              <value>2018-11-07T00:00Z</value>
            </time>
            <data xsi:type="ITEM_TREE" archetype_node_id="at0003">
              <name>
                <value>Tree</value>
              </name>
              <items xsi:type="ELEMENT" archetype_node_id="at0005">
                <name>
                  <value>Test name</value>
                </name>
                <value xsi:type="DV_TEXT">
                  <value>Histopathology analysis</value>
                </value>
              </items>
              <items xsi:type="CLUSTER" archetype_node_id="openEHR-EHR-CLUSTER.anatomical_pathology_exam.v0">
                <name>
                  <value>Anatomical pathology examination</value>
                </name>
                <items xsi:type="CLUSTER" archetype_node_id="at0005">
                  <name>
                    <value>Anatomical pathology finding</value>
                  </name>
                  <items xsi:type="CLUSTER" archetype_node_id="openEHR-EHR-CLUSTER.media_file.v1">
                    <name>
                      <value>Media file</value>
                    </name>
                    <items xsi:type="ELEMENT" archetype_node_id="at0007">
                      <name>
                        <value>Availability digital imaging</value>
                      </name>
                      <value xsi:type="DV_TEXT">
                        <value>Can be generated</value>
                      </value>
                    </items>
                  </items>
                </items>
              </items>
              <items xsi:type="CLUSTER" archetype_node_id="openEHR-EHR-CLUSTER.anatomical_pathology_exam.v0">
                <name>
                  <value>Invasion front</value>
                </name>
                <items xsi:type="CLUSTER" archetype_node_id="at0005">
                  <name>
                    <value>Anatomical pathology finding</value>
                  </name>
                  <items xsi:type="CLUSTER" archetype_node_id="openEHR-EHR-CLUSTER.media_file.v1">
                    <name>
                      <value>Digital imaging invasion front</value>
                    </name>
                    <items xsi:type="ELEMENT" archetype_node_id="at0007">
                      <name>
                        <value>Availability invasion front digital imaging</value>
                      </name>
                      <value xsi:type="DV_TEXT">
                        <value>Can be generated</value>
                      </value>
                    </items>
                  </items>
                </items>
              </items>
            </data>
          </events>
        </data>
      </items>
    </items>
  </content>
  <content xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:type="SECTION" archetype_node_id="openEHR-EHR-SECTION.result_details.v0">
    <name>
      <value>Molecular markers</value>
    </name>
    <items xsi:type="SECTION" archetype_node_id="at0002">
      <name>
        <value>Result group</value>
      </name>
      <items xsi:type="OBSERVATION" archetype_node_id="openEHR-EHR-OBSERVATION.laboratory_test_result.v1">
        <name>
          <value>Oncogenic mutations test</value>
        </name>
        <archetype_details>
          <archetype_id>
            <value>openEHR-EHR-OBSERVATION.laboratory_test_result.v1</value>
            <qualifiedRmEntity>openEHR-EHR-OBSERVATION</qualifiedRmEntity>
            <domainConcept>laboratory_test_result</domainConcept>
            <rmOriginator>openEHR</rmOriginator>
            <rmName>EHR</rmName>
            <rmEntity>OBSERVATION</rmEntity>
            <versionId>1</versionId>
          </archetype_id>
          <template_id>
            <value>pippo</value>
          </template_id>
          <rm_version>1.0.4</rm_version>
        </archetype_details>
        <language>
          <terminology_id>
            <value>ISO_639-1</value>
          </terminology_id>
          <code_string>en</code_string>
        </language>
        <encoding>
          <terminology_id>
            <value>IANA_character-sets</value>
          </terminology_id>
          <code_string>UTF-8</code_string>
        </encoding>
        <subject xsi:type="PARTY_SELF"/>
        <data archetype_node_id="at0001">
          <name>
            <value>Event Series</value>
          </name>
          <origin>
            <value>9999-12-10T00:00Z</value>
          </origin>
          <events xsi:type="POINT_EVENT" archetype_node_id="at0002">
            <name>
              <value>Any event</value>
            </name>
            <time>
              <value>9999-12-10T00:00Z</value>
            </time>
            <data xsi:type="ITEM_TREE" archetype_node_id="at0003">
              <name>
                <value>Tree</value>
              </name>
              <items xsi:type="ELEMENT" archetype_node_id="at0005">
                <name>
                  <value>Test name</value>
                </name>
                <value xsi:type="DV_TEXT">
                  <value>BRAF, PIC3CA, HER2 mutation test</value>
                </value>
              </items>
              <items xsi:type="ELEMENT" archetype_node_id="at0057">
                <name>
                  <value>BRAF, PIC3CA, HER2 mutation status</value>
                </name>
                <value xsi:type="DV_TEXT">
                  <value>Not done</value>
                </value>
              </items>
            </data>
          </events>
        </data>
      </items>
      <items xsi:type="OBSERVATION" archetype_node_id="openEHR-EHR-OBSERVATION.laboratory_test_result.v1">
        <name>
          <value>Microsatellites instability analysis</value>
        </name>
        <archetype_details>
          <archetype_id>
            <value>openEHR-EHR-OBSERVATION.laboratory_test_result.v1</value>
            <qualifiedRmEntity>openEHR-EHR-OBSERVATION</qualifiedRmEntity>
            <domainConcept>laboratory_test_result</domainConcept>
            <rmOriginator>openEHR</rmOriginator>
            <rmName>EHR</rmName>
            <rmEntity>OBSERVATION</rmEntity>
            <versionId>1</versionId>
          </archetype_id>
          <template_id>
            <value>pippo</value>
          </template_id>
          <rm_version>1.0.4</rm_version>
        </archetype_details>
        <language>
          <terminology_id>
            <value>ISO_639-1</value>
          </terminology_id>
          <code_string>en</code_string>
        </language>
        <encoding>
          <terminology_id>
            <value>IANA_character-sets</value>
          </terminology_id>
          <code_string>UTF-8</code_string>
        </encoding>
        <subject xsi:type="PARTY_SELF"/>
        <data archetype_node_id="at0001">
          <name>
            <value>Event Series</value>
          </name>
          <origin>
            <value>9999-12-10T00:00Z</value>
          </origin>
          <events xsi:type="POINT_EVENT" archetype_node_id="at0002">
            <name>
              <value>Any event</value>
            </name>
            <time>
              <value>9999-12-10T00:00Z</value>
            </time>
            <data xsi:type="ITEM_TREE" archetype_node_id="at0003">
              <name>
                <value>Tree</value>
              </name>
              <items xsi:type="ELEMENT" archetype_node_id="at0005">
                <name>
                  <value>Test name</value>
                </name>
                <value xsi:type="DV_TEXT">
                  <value>Microsatellite instability test</value>
                </value>
              </items>
              <items xsi:type="ELEMENT" archetype_node_id="at0057">
                <name>
                  <value>Microsatellite instability</value>
                </name>
                <value xsi:type="DV_TEXT">
                  <value>Not done</value>
                </value>
              </items>
            </data>
          </events>
        </data>
      </items>
      <items xsi:type="OBSERVATION" archetype_node_id="openEHR-EHR-OBSERVATION.laboratory_test_result.v1">
        <name>
          <value>KRAS mutation status</value>
        </name>
        <archetype_details>
          <archetype_id>
            <value>openEHR-EHR-OBSERVATION.laboratory_test_result.v1</value>
            <qualifiedRmEntity>openEHR-EHR-OBSERVATION</qualifiedRmEntity>
            <domainConcept>laboratory_test_result</domainConcept>
            <rmOriginator>openEHR</rmOriginator>
            <rmName>EHR</rmName>
            <rmEntity>OBSERVATION</rmEntity>
            <versionId>1</versionId>
          </archetype_id>
          <template_id>
            <value>pippo</value>
          </template_id>
          <rm_version>1.0.4</rm_version>
        </archetype_details>
        <language>
          <terminology_id>
            <value>ISO_639-1</value>
          </terminology_id>
          <code_string>en</code_string>
        </language>
        <encoding>
          <terminology_id>
            <value>IANA_character-sets</value>
          </terminology_id>
          <code_string>UTF-8</code_string>
        </encoding>
        <subject xsi:type="PARTY_SELF"/>
        <data archetype_node_id="at0001">
          <name>
            <value>Event Series</value>
          </name>
          <origin>
            <value>9999-12-10T00:00Z</value>
          </origin>
          <events xsi:type="POINT_EVENT" archetype_node_id="at0002">
            <name>
              <value>Any event</value>
            </name>
            <time>
              <value>9999-12-10T00:00Z</value>
            </time>
            <data xsi:type="ITEM_TREE" archetype_node_id="at0003">
              <name>
                <value>Tree</value>
              </name>
              <items xsi:type="ELEMENT" archetype_node_id="at0005">
                <name>
                  <value>Test name</value>
                </name>
                <value xsi:type="DV_TEXT">
                  <value>KRAS mutation test</value>
                </value>
              </items>
              <items xsi:type="CLUSTER" archetype_node_id="openEHR-EHR-CLUSTER.genetic_variant_presence.v0">
                <name>
                  <value>NRAS exon 4 (codons 117 or 146)</value>
                </name>
                <items xsi:type="ELEMENT" archetype_node_id="at0001">
                  <name>
                    <value>Variant name</value>
                  </name>
                  <value xsi:type="DV_TEXT">
                    <value>NRAS exon 4 (codons 117 or 146)</value>
                  </value>
                </items>
                <items xsi:type="ELEMENT" archetype_node_id="at0002">
                  <name>
                    <value>NRAS exon 4 (codons 117 or 146)</value>
                  </name>
                  <value xsi:type="DV_CODED_TEXT">
                    <value>Indeterminate</value>
                    <defining_code>
                      <terminology_id>
                        <value>local</value>
                      </terminology_id>
                      <code_string>at0007</code_string>
                    </defining_code>
                  </value>
                </items>
              </items>
              <items xsi:type="CLUSTER" archetype_node_id="openEHR-EHR-CLUSTER.genetic_variant_presence.v0">
                <name>
                  <value>NRAS exon 3 (codons 59 or 61)</value>
                </name>
                <items xsi:type="ELEMENT" archetype_node_id="at0001">
                  <name>
                    <value>Variant name</value>
                  </name>
                  <value xsi:type="DV_TEXT">
                    <value>NRAS exon 3 (codons 59 or 61)</value>
                  </value>
                </items>
                <items xsi:type="ELEMENT" archetype_node_id="at0002">
                  <name>
                    <value>NRAS exon 3 (codons 59 or 61)</value>
                  </name>
                  <value xsi:type="DV_CODED_TEXT">
                    <value>Indeterminate</value>
                    <defining_code>
                      <terminology_id>
                        <value>local</value>
                      </terminology_id>
                      <code_string>at0007</code_string>
                    </defining_code>
                  </value>
                </items>
              </items>
              <items xsi:type="CLUSTER" archetype_node_id="openEHR-EHR-CLUSTER.genetic_variant_presence.v0">
                <name>
                  <value>NRAS exon 2 (codons 12 or 13)</value>
                </name>
                <items xsi:type="ELEMENT" archetype_node_id="at0001">
                  <name>
                    <value>Variant name</value>
                  </name>
                  <value xsi:type="DV_TEXT">
                    <value>NRAS exon 2 (codons 12 or 13)</value>
                  </value>
                </items>
                <items xsi:type="ELEMENT" archetype_node_id="at0002">
                  <name>
                    <value>NRAS exon 2 (codons 12 or 13)</value>
                  </name>
                  <value xsi:type="DV_CODED_TEXT">
                    <value>Indeterminate</value>
                    <defining_code>
                      <terminology_id>
                        <value>local</value>
                      </terminology_id>
                      <code_string>at0007</code_string>
                    </defining_code>
                  </value>
                </items>
              </items>
              <items xsi:type="CLUSTER" archetype_node_id="openEHR-EHR-CLUSTER.genetic_variant_presence.v0">
                <name>
                  <value>KRAS exon 4 (codons 117 or 146)</value>
                </name>
                <items xsi:type="ELEMENT" archetype_node_id="at0001">
                  <name>
                    <value>Variant name</value>
                  </name>
                  <value xsi:type="DV_TEXT">
                    <value>KRAS exon 4 (codons 117 or 146)</value>
                  </value>
                </items>
                <items xsi:type="ELEMENT" archetype_node_id="at0002">
                  <name>
                    <value>KRAS exon 4 (codons 117 or 146)</value>
                  </name>
                  <value xsi:type="DV_CODED_TEXT">
                    <value>Indeterminate</value>
                    <defining_code>
                      <terminology_id>
                        <value>local</value>
                      </terminology_id>
                      <code_string>at0007</code_string>
                    </defining_code>
                  </value>
                </items>
              </items>
              <items xsi:type="CLUSTER" archetype_node_id="openEHR-EHR-CLUSTER.genetic_variant_presence.v0">
                <name>
                  <value>KRAS exon 3 (codons 59 or 61)</value>
                </name>
                <items xsi:type="ELEMENT" archetype_node_id="at0001">
                  <name>
                    <value>Variant name</value>
                  </name>
                  <value xsi:type="DV_TEXT">
                    <value>KRAS exon 3 (codons 59 or 61)</value>
                  </value>
                </items>
                <items xsi:type="ELEMENT" archetype_node_id="at0002">
                  <name>
                    <value>KRAS exon 3 (codons 59 or 61)</value>
                  </name>
                  <value xsi:type="DV_CODED_TEXT">
                    <value>Indeterminate</value>
                    <defining_code>
                      <terminology_id>
                        <value>local</value>
                      </terminology_id>
                      <code_string>at0007</code_string>
                    </defining_code>
                  </value>
                </items>
              </items>
              <items xsi:type="CLUSTER" archetype_node_id="openEHR-EHR-CLUSTER.genetic_variant_presence.v0">
                <name>
                  <value>KRAS exon 2 (codons 12 or 13)</value>
                </name>
                <items xsi:type="ELEMENT" archetype_node_id="at0001">
                  <name>
                    <value>Variant name</value>
                  </name>
                  <value xsi:type="DV_TEXT">
                    <value>KRAS exon 2 (codons 12 or 13)</value>
                  </value>
                </items>
                <items xsi:type="ELEMENT" archetype_node_id="at0002">
                  <name>
                    <value>KRAS exon 2 (codons 12 or 13)</value>
                  </name>
                  <value xsi:type="DV_CODED_TEXT">
                    <value>Indeterminate</value>
                    <defining_code>
                      <terminology_id>
                        <value>local</value>
                      </terminology_id>
                      <code_string>at0007</code_string>
                    </defining_code>
                  </value>
                </items>
              </items>
            </data>
          </events>
        </data>
      </items>
      <items xsi:type="OBSERVATION" archetype_node_id="openEHR-EHR-OBSERVATION.laboratory_test_result.v1">
        <name>
          <value>Mismatch repair gene analysis</value>
        </name>
        <archetype_details>
          <archetype_id>
            <value>openEHR-EHR-OBSERVATION.laboratory_test_result.v1</value>
            <qualifiedRmEntity>openEHR-EHR-OBSERVATION</qualifiedRmEntity>
            <domainConcept>laboratory_test_result</domainConcept>
            <rmOriginator>openEHR</rmOriginator>
            <rmName>EHR</rmName>
            <rmEntity>OBSERVATION</rmEntity>
            <versionId>1</versionId>
          </archetype_id>
          <template_id>
            <value>pippo</value>
          </template_id>
          <rm_version>1.0.4</rm_version>
        </archetype_details>
        <language>
          <terminology_id>
            <value>ISO_639-1</value>
          </terminology_id>
          <code_string>en</code_string>
        </language>
        <encoding>
          <terminology_id>
            <value>IANA_character-sets</value>
          </terminology_id>
          <code_string>UTF-8</code_string>
        </encoding>
        <subject xsi:type="PARTY_SELF"/>
        <data archetype_node_id="at0001">
          <name>
            <value>Event Series</value>
          </name>
          <origin>
            <value>9999-12-10T00:00Z</value>
          </origin>
          <events xsi:type="POINT_EVENT" archetype_node_id="at0002">
            <name>
              <value>Any event</value>
            </name>
            <time>
              <value>9999-12-10T00:00Z</value>
            </time>
            <data xsi:type="ITEM_TREE" archetype_node_id="at0003">
              <name>
                <value>Tree</value>
              </name>
              <items xsi:type="ELEMENT" archetype_node_id="at0005">
                <name>
                  <value>Test name</value>
                </name>
                <value xsi:type="DV_TEXT">
                  <value>Mismatch repair gene expression</value>
                </value>
              </items>
              <items xsi:type="ELEMENT" archetype_node_id="at0057">
                <name>
                  <value>Mismatch repair gene expression</value>
                </name>
                <value xsi:type="DV_TEXT">
                  <value>Not done</value>
                </value>
              </items>
            </data>
          </events>
        </data>
      </items>
    </items>
  </content>
  <content xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:type="SECTION" archetype_node_id="openEHR-EHR-SECTION.demographics_rcp.v1">
    <name>
      <value>Patient data</value>
    </name>
    <items xsi:type="EVALUATION" archetype_node_id="openEHR-EHR-EVALUATION.gender.v1">
      <name>
        <value>Gender</value>
      </name>
      <archetype_details>
        <archetype_id>
          <value>openEHR-EHR-EVALUATION.gender.v1</value>
          <qualifiedRmEntity>openEHR-EHR-EVALUATION</qualifiedRmEntity>
          <domainConcept>gender</domainConcept>
          <rmOriginator>openEHR</rmOriginator>
          <rmName>EHR</rmName>
          <rmEntity>EVALUATION</rmEntity>
          <versionId>1</versionId>
        </archetype_id>
        <template_id>
          <value>pippo</value>
        </template_id>
        <rm_version>1.0.4</rm_version>
      </archetype_details>
      <language>
        <terminology_id>
          <value>ISO_639-1</value>
        </terminology_id>
        <code_string>en</code_string>
      </language>
      <encoding>
        <terminology_id>
          <value>IANA_character-sets</value>
        </terminology_id>
        <code_string>UTF-8</code_string>
      </encoding>
      <subject xsi:type="PARTY_SELF"/>
      <data xsi:type="ITEM_TREE" archetype_node_id="at0002">
        <name>
          <value>Tree</value>
        </name>
        <items xsi:type="ELEMENT" archetype_node_id="at0019">
          <name>
            <value>Biological sex</value>
          </name>
          <value xsi:type="DV_CODED_TEXT">
            <value>FEMALE</value>
            <defining_code>
              <terminology_id>
                <value>omop_vocabulary</value>
              </terminology_id>
              <code_string>8532</code_string>
            </defining_code>
          </value>
        </items>
      </data>
    </items>
    <items xsi:type="EVALUATION" archetype_node_id="openEHR-EHR-EVALUATION.problem_diagnosis.v1">
      <name>
        <value>Primary diagnosis</value>
      </name>
      <archetype_details>
        <archetype_id>
          <value>openEHR-EHR-EVALUATION.problem_diagnosis.v1</value>
          <qualifiedRmEntity>openEHR-EHR-EVALUATION</qualifiedRmEntity>
          <domainConcept>problem_diagnosis</domainConcept>
          <rmOriginator>openEHR</rmOriginator>
          <rmName>EHR</rmName>
          <rmEntity>EVALUATION</rmEntity>
          <versionId>1</versionId>
        </archetype_id>
        <template_id>
          <value>pippo</value>
        </template_id>
        <rm_version>1.0.4</rm_version>
      </archetype_details>
      <language>
        <terminology_id>
          <value>ISO_639-1</value>
        </terminology_id>
        <code_string>en</code_string>
      </language>
      <encoding>
        <terminology_id>
          <value>IANA_character-sets</value>
        </terminology_id>
        <code_string>UTF-8</code_string>
      </encoding>
      <subject xsi:type="PARTY_SELF"/>
      <data xsi:type="ITEM_TREE" archetype_node_id="at0001">
        <name>
          <value>structure</value>
        </name>
        <items xsi:type="ELEMENT" archetype_node_id="at0002">
          <name>
            <value>Primary diagnosis</value>
          </name>
          <value xsi:type="DV_CODED_TEXT">
            <value>Colorectal cancer</value>
            <defining_code>
              <terminology_id>
                <value>omop_vocabulary</value>
              </terminology_id>
              <code_string>44803809</code_string>
            </defining_code>
          </value>
        </items>
        <items xsi:type="ELEMENT" archetype_node_id="at0003">
          <name>
            <value>Date of diagnosis</value>
          </name>
          <value xsi:type="DV_DATE_TIME">
            <value>2022-03-01T00:00Z</value>
          </value>
        </items>
        <items xsi:type="CLUSTER" archetype_node_id="openEHR-EHR-CLUSTER.timing_nondaily.v1">
          <name>
            <value>Diagnosis timing</value>
          </name>
          <items xsi:type="CLUSTER" archetype_node_id="at0006">
            <name>
              <value>Primary diagnosis</value>
            </name>
            <items xsi:type="ELEMENT" archetype_node_id="at0009">
              <name>
                <value>Age at diagnosis</value>
              </name>
              <value xsi:type="DV_DURATION">
                <value>P55Y</value>
              </value>
            </items>
          </items>
        </items>
      </data>
    </items>
    <items xsi:type="EVALUATION" archetype_node_id="openEHR-EHR-EVALUATION.problem_diagnosis.v1">
      <name>
        <value>Metastasis diagnosis</value>
      </name>
      <archetype_details>
        <archetype_id>
          <value>openEHR-EHR-EVALUATION.problem_diagnosis.v1</value>
          <qualifiedRmEntity>openEHR-EHR-EVALUATION</qualifiedRmEntity>
          <domainConcept>problem_diagnosis</domainConcept>
          <rmOriginator>openEHR</rmOriginator>
          <rmName>EHR</rmName>
          <rmEntity>EVALUATION</rmEntity>
          <versionId>1</versionId>
        </archetype_id>
        <template_id>
          <value>pippo</value>
        </template_id>
        <rm_version>1.0.4</rm_version>
      </archetype_details>
      <language>
        <terminology_id>
          <value>ISO_639-1</value>
        </terminology_id>
        <code_string>en</code_string>
      </language>
      <encoding>
        <terminology_id>
          <value>IANA_character-sets</value>
        </terminology_id>
        <code_string>UTF-8</code_string>
      </encoding>
      <subject xsi:type="PARTY_SELF"/>
      <data xsi:type="ITEM_TREE" archetype_node_id="at0001">
        <name>
          <value>structure</value>
        </name>
        <items xsi:type="ELEMENT" archetype_node_id="at0002">
          <name>
            <value>Metastasis diagnosis</value>
          </name>
          <value xsi:type="DV_CODED_TEXT">
            <value>Metastasis</value>
            <defining_code>
              <terminology_id>
                <value>omop_vocabulary</value>
              </terminology_id>
              <code_string>36769180</code_string>
            </defining_code>
          </value>
        </items>
        <items xsi:type="CLUSTER" archetype_node_id="openEHR-EHR-CLUSTER.timing_nondaily.v1">
          <name>
            <value>Metastasis diagnosis</value>
          </name>
          <items xsi:type="CLUSTER" archetype_node_id="at0006">
            <name>
              <value>Metastasis diagnosis</value>
            </name>
            <items xsi:type="ELEMENT" archetype_node_id="at0005">
              <name>
                <value>From event</value>
              </name>
              <value xsi:type="DV_TEXT">
                <value>Primary diagnosis</value>
              </value>
            </items>
            <items xsi:type="ELEMENT" archetype_node_id="at0009">
              <name>
                <value>Time of recurrence</value>
              </name>
              <value xsi:type="DV_DURATION">
                <value>P784D</value>
              </value>
            </items>
          </items>
        </items>
      </data>
    </items>
  </content>
</composition>
    '''
    xml_parser = etree.XMLParser(remove_blank_text=True,
                                     remove_comments=False,
                                     remove_pis=False)    
    firstxml=etree.fromstring(xml1,xml_parser)
    secondxml=etree.fromstring(xml2,xml_parser)
    difference=myutils.compare_xmls(firstxml,secondxml)
    assert len(difference)==5
    assert '+<value>0c770609-2ded-4c0f-aa7b-9b9352f6c90c::local.ehrbase.org::1</value>' in difference[1]
    assert '-<value>P1W</value>' in difference[2]
    assert '-<value>P65W</value>' in difference[3]
    assert '-<value>P112W</value>' in difference[4]
    
    ndiff=myutils.analyze_comparison_xml(difference)
    assert ndiff==0
    