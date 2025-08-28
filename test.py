import yaml, re
from pathlib import Path

CONFIG_PATH = Path("config.yaml")

# Your list of Irish IT companies
companies = [
"Microsoft", "Dell Ireland", "Apple Ireland", "Oracle", "Facebook",
"Sandisk", "Kingston", "VMware", "Intel Ireland", "Maxim Integrated Products",
"Eircom", "HP Ireland", "NCR", "Sandvik", "Emc", "Netgear International",
"Synopsys", "SAP Business Objects", "Altera", "Microchip Technology",
"CarTrawler", "IBM", "Cadence", "Xilinx", "BT", "Gartner", "VCE",
"Skillsoft", "Yahoo! Ireland", "Virgin Media", "QLogic", "Red Hat",
"Analog Devices", "Salesforce", "Teradata", "Nuance Communications", "Fónua",
"Mentor Graphics", "Ericsson", "Bentley Software", "First Data", "Fleetmatics Group",
"Microfocus", "Ptc software", "Zynga", "Xerox", "Linkedin", "Twitter",
"Orange Business Services", "BMC", "Accenture", "Capita Managed IT Solutions",
"CMS Distribution", "IAC Search & Media", "CMS Peripherals", "Taxback Group",
"PTC Ireland", "Honeywell Process Solutions", "Trend Micro", "Extreme Networks",
"Transas Marine", "Websense", "Commscope", "Workday", "M/A-COM Technology Solutions",
"Stratus Technologies", "Humax", "First Derivatives", "ABB Ltd", "Allstate NI",
"Arvato", "Fidelity Investments Ireland", "Molex", "Openet", "Cognex", "Monex",
"Dialogic", "Westcoast", "Microwarehouse", "Schlumberger Information Solutions",
"Premiere Conferencing", "Cross Refrigeration", "Afilias", "Siemens",
"Citrix Systems Ireland", "Arvato Digital Services", "Cisco", "Version1",
"Global Cloud Xchange", "G4S Secure Solutions", "Fujitsu Ireland", "J2 Global",
"Digital River", "GE Sensing", "Pramerica", "DTS", "NetIQ Europe", "Logmein",
"PFH", "Dropbox Ireland", "Abtran", "Matrox", "Leaseplan Information Services",
"Dk Donohoe", "Ewl Electric", "Avocent", "Amt-Sybex", "Volex", "Fineos",
"Conversant Media", "Datalex", "Verizon Ireland", "3M Ireland", "Quantcast International",
"Rigney Dolphin", "ITG Europe", "Imagine Communications", "Corvil", "Populis Ireland",
"Creative Labs", "Intuition Publishing", "Zamano", "Convergys", "AOL Global Operations",
"Asset Control", "Logicalis", "Electronic Arts", "Harkness Screens International",
"Guidewire Software", "Alcatel-Lucent", "BAE Systems Detica", "Airspeed Communications",
"Unity Technology Solutions", "CSG International", "Option", "Moneymate", "Ion Trading"
]

# Load or create config.yaml
cfg = {}
if CONFIG_PATH.exists():
    cfg = yaml.safe_load(CONFIG_PATH.read_text()) or {}

if 'greenhouse_companies' not in cfg: cfg['greenhouse_companies'] = []
if 'lever_companies' not in cfg: cfg['lever_companies'] = []

# Populate companies with slugs
for c in companies:
    slug = re.sub(r'[^a-z0-9]+', '-', c.lower()).strip('-')
    if not any(d.get('slug') == slug for d in cfg['greenhouse_companies']):
        cfg['greenhouse_companies'].append({'slug': slug, 'website': ''})
    if not any(d.get('slug') == slug for d in cfg['lever_companies']):
        cfg['lever_companies'].append({'slug': slug})

CONFIG_PATH.write_text(yaml.dump(cfg))
print(f"Added {len(companies)} companies to config.yaml")
