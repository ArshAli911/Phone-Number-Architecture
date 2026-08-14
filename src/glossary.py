# -*- coding: utf-8 -*-
"""Glossary source for the appendix.

Each entry: key -> (headword, expansion|'', definition)
`key` is what is searched for in the volume text (word-boundary, case-sensitive
for acronyms, case-insensitive for the lower-case concept phrases).
"""

ACRONYMS = {
 # --- numbering & identity -------------------------------------------------
 'E.164': ('E.164', 'ITU-T Recommendation E.164',
   'The international public telecommunication numbering plan. Defines the structure of '
   'international numbers as a country code followed by a national significant number, '
   'historically within a 15-digit maximum.'),
 'MSISDN': ('MSISDN', 'Mobile Station International Subscriber Directory Number',
   'The dialable telephone number attached to a mobile subscription — the number the '
   'outside world knows. It is a service identifier, not a device address.'),
 'IMSI': ('IMSI', 'International Mobile Subscriber Identity',
   'The permanent identity of a subscription, stored on the SIM. Composed of MCC, MNC and '
   'MSIN. Normally never revealed to the caller and increasingly replaced on the air '
   'interface by temporary identities.'),
 'SUPI': ('SUPI', 'Subscription Permanent Identifier',
   'The 5G equivalent of the IMSI. In 5G it is not sent in the clear over the radio; a '
   'concealed form is used during initial registration.'),
 'GUTI': ('5G-GUTI', 'Globally Unique Temporary Identity',
   'A temporary identity allocated by the AMF and used in place of the SUPI for most '
   'signalling, so the permanent identity is rarely broadcast.'),
 'IMEI': ('IMEI', 'International Mobile Equipment Identity',
   'Identifies the handset hardware rather than the subscriber. Moving a SIM to another '
   'phone changes the IMEI while the IMSI and MSISDN stay the same.'),
 'ICCID': ('ICCID', 'Integrated Circuit Card Identifier',
   'The serial number of the physical SIM card itself, distinct from the subscriber '
   'identity stored on it.'),
 'MCC': ('MCC', 'Mobile Country Code',
   'The leading field of an IMSI identifying the subscriber\u2019s home country.'),
 'MNC': ('MNC', 'Mobile Network Code',
   'The field following the MCC that identifies the home operator within that country.'),
 'MSIN': ('MSIN', 'Mobile Subscriber Identification Number',
   'The operator-assigned portion of an IMSI that identifies the individual subscription.'),
 'NSN': ('NSN', 'National Significant Number',
   'The part of an international number that follows the country code.'),
 'NANP': ('NANP', 'North American Numbering Plan',
   'The shared numbering plan for the United States, Canada and several other territories, '
   'reached with country code +1 and structured as NPA-NXX-XXXX.'),
 'NPA': ('NPA', 'Numbering Plan Area',
   'The area code in the NANP — the first three digits of a ten-digit number.'),
 'NXX': ('NXX', '',
   'The central-office or exchange prefix in a NANP number: the second group of three digits.'),
 'MNP': ('MNP', 'Mobile Number Portability',
   'The arrangement that lets a subscriber keep a telephone number when changing operator, '
   'breaking the old assumption that a number prefix identifies the serving network.'),
 'ITU': ('ITU', 'International Telecommunication Union',
   'The United Nations agency that allocates international numbering resources and '
   'publishes the E-series numbering recommendations.'),
 'ITU-T': ('ITU-T', 'ITU Telecommunication Standardization Sector',
   'The branch of the ITU that issues telecommunication standards, including E.164.'),
 'NANPA': ('NANPA', 'North American Numbering Plan Administrator',
   'The body that administers number resources within the NANP.'),
 'TRAI': ('TRAI', 'Telecom Regulatory Authority of India',
   'India\u2019s telecommunications regulator, responsible among other things for the mobile '
   'number portability framework.'),
 'FCC': ('FCC', 'Federal Communications Commission',
   'The United States communications regulator.'),
 'GSMA': ('GSMA', 'GSM Association',
   'The industry body representing mobile operators; maintains a number of mobile identity '
   'and interconnect specifications.'),
 'ETSI': ('ETSI', 'European Telecommunications Standards Institute',
   'European standards body, a founding partner of 3GPP.'),
 'IoT': ('IoT / M2M', 'Internet of Things / machine-to-machine',
   'Categories of non-human subscriptions for which dedicated numbering ranges have been '
   'defined in recent revisions of E.164.'),

 # --- legacy switching -----------------------------------------------------
 'PSTN': ('PSTN', 'Public Switched Telephone Network',
   'The traditional circuit-switched telephone network. Modern IP telephony still '
   'interworks with it through gateways.'),
 'ISDN': ('ISDN', 'Integrated Services Digital Network',
   'A digital circuit-switched successor to analogue subscriber lines, carrying voice and '
   'data over the same access.'),
 'PBX': ('PBX', 'Private Branch Exchange',
   'A private switch inside an organisation, allowing one external number to reach many '
   'internal endpoints.'),
 'DS0': ('DS0', '',
   'A single 64 kbit/s digital voice channel — 8 kHz sampling at 8 bits per sample — the '
   'basic unit multiplexed onto TDM trunks.'),
 'PCM': ('PCM', 'Pulse-Code Modulation',
   'The sampling-and-quantisation scheme that turns an analogue voice signal into the '
   'classic 64 kbit/s digital stream.'),
 'TDM': ('TDM', 'Time-Division Multiplexing',
   'Carrying many fixed-rate channels on one trunk by giving each a repeating time slot.'),
 'DTMF': ('DTMF', 'Dual-Tone Multi-Frequency',
   'Touch-tone signalling: each digit is sent as a pair of audio tones, replacing the pulse '
   'counting of rotary dials.'),
 'SS7': ('SS7', 'Signalling System No. 7',
   'The out-of-band signalling network of the digital PSTN and of 2G/3G mobile networks. It '
   'separates call control from the voice path and carries database queries such as '
   'roaming and portability lookups.'),
 'MSC': ('MSC', 'Mobile Switching Centre',
   'The circuit-switched call-control and switching node of GSM-era networks. It has no '
   'single successor in 5G: its duties are split across the AMF, SMF, UPF and IMS.'),
 'HLR': ('HLR', 'Home Location Register',
   'The master subscriber database of a GSM network, holding subscription data and a '
   'pointer to where the subscriber is currently registered.'),
 'VLR': ('VLR', 'Visitor Location Register',
   'A local database holding temporary records for subscribers currently attached to a '
   'given serving area.'),
 'AuC': ('AuC', 'Authentication Centre',
   'The GSM-era node holding the secret keys used to authenticate SIMs.'),
 'BTS': ('BTS', 'Base Transceiver Station',
   'The GSM radio site — the equipment that actually transmits and receives over the air.'),
 'BSC': ('BSC', 'Base Station Controller',
   'The GSM node controlling a group of base stations, handling radio resources and '
   'handovers between them.'),
 'GSM': ('GSM', 'Global System for Mobile Communications',
   'The second-generation digital cellular standard that introduced the SIM, the IMSI and '
   'the HLR/VLR mobility model.'),
 'IVR': ('IVR', 'Interactive Voice Response',
   'An automated system that answers a call and routes or serves the caller by menu.'),

 # --- IP telephony ---------------------------------------------------------
 'VoIP': ('VoIP', 'Voice over IP',
   'Carrying telephone speech as packets over an IP network rather than over a dedicated '
   'circuit.'),
 'SIP': ('SIP', 'Session Initiation Protocol',
   'The text-based signalling protocol (RFC 3261) used to create, modify and terminate '
   'multimedia sessions. It sets up the call but carries none of the audio.'),
 'SDP': ('SDP', 'Session Description Protocol',
   'The payload format (RFC 4566) carried inside SIP messages that describes the media a '
   'party can send and receive: addresses, ports, codecs and direction.'),
 'RTP': ('RTP', 'Real-time Transport Protocol',
   'The protocol (RFC 3550) that carries the actual media. Its header supplies a sequence '
   'number, a timestamp and an SSRC so the receiver can reorder, time and separate streams.'),
 'RTCP': ('RTCP', 'RTP Control Protocol',
   'The companion to RTP that carries no media but reports on it — loss, jitter and '
   'round-trip time — so senders can adapt.'),
 'SSRC': ('SSRC', 'Synchronisation Source',
   'The 32-bit identifier in an RTP header that distinguishes one media stream from another '
   'within the same session.'),
 'URI': ('URI', 'Uniform Resource Identifier',
   'The addressing form used by SIP, e.g. sip:+919876543210@ims.example.com — a logical '
   'destination, not an IP address.'),
 'IMS': ('IMS', 'IP Multimedia Subsystem',
   'The standardised SIP-based service core that operators use to deliver voice and other '
   'multimedia over their packet networks, and to interwork with the PSTN.'),
 'CSCF': ('CSCF', 'Call Session Control Function',
   'The family of SIP servers at the heart of IMS: the proxy (P-CSCF), interrogating '
   '(I-CSCF) and serving (S-CSCF) roles.'),
 'P-CSCF': ('P-CSCF', 'Proxy CSCF',
   'The subscriber\u2019s first point of contact with IMS. All SIP traffic from the device '
   'passes through it, and it triggers the QoS treatment for the media.'),
 'I-CSCF': ('I-CSCF', 'Interrogating CSCF',
   'The entry point into an operator\u2019s IMS from outside. It queries the subscriber '
   'database to find which S-CSCF is serving the destination.'),
 'S-CSCF': ('S-CSCF', 'Serving CSCF',
   'The central registrar and service-control node for a subscriber. It holds the '
   'registration, applies service logic and routes requests onward.'),
 'TAS': ('TAS', 'Telephony Application Server',
   'The IMS application server that implements telephony features — call forwarding, '
   'barring, conferencing, voicemail diversion.'),
 'HSS': ('HSS', 'Home Subscriber Server',
   'The IMS/LTE subscriber database holding authentication data, service profiles and '
   'registration state.'),
 'VoLTE': ('VoLTE', 'Voice over LTE',
   'Voice carried as IMS-controlled packets over a 4G LTE radio and core network.'),
 'VoNR': ('VoNR', 'Voice over New Radio',
   'The 5G Standalone equivalent: IMS voice carried over 5G NR with a 5G core.'),
 'RFC': ('RFC', 'Request for Comments',
   'The document series in which IETF internet standards such as SIP, SDP and RTP are '
   'published.'),

 # --- 4G / 5G --------------------------------------------------------------
 'UE': ('UE', 'User Equipment',
   'The 3GPP term for the subscriber\u2019s device — handset plus SIM/USIM.'),
 'NR': ('NR', 'New Radio',
   'The 5G radio access technology.'),
 'SA': ('5G SA', '5G Standalone',
   'A 5G deployment using a 5G core as well as 5G radio, as opposed to non-standalone '
   'deployments that anchor on the LTE core.'),
 'RAN': ('RAN', 'Radio Access Network',
   'The radio side of a mobile network: the base stations and the protocols between them '
   'and the device.'),
 'gNB': ('gNB', '',
   'The 5G base station. It terminates the radio protocol stack and connects to the core '
   'over N2 (control) and N3 (user plane).'),
 'eNB': ('eNB', '',
   'The LTE base station, the 4G counterpart of the gNB.'),
 'EPC': ('EPC', 'Evolved Packet Core',
   'The 4G core network, comprising MME, SGW and PGW among others.'),
 '5GC': ('5GC', '5G Core',
   'The service-based 5G core network: AMF, SMF, UPF, UDM, AUSF, PCF and others, '
   'communicating over HTTP/2 APIs.'),
 'AMF': ('AMF', 'Access and Mobility Management Function',
   'The 5G core function that terminates NAS signalling, manages registration, '
   'authentication and mobility, and handles paging. It is control plane only — no user '
   'traffic passes through it.'),
 'SMF': ('SMF', 'Session Management Function',
   'Manages PDU sessions: IP address allocation, session establishment and the forwarding '
   'rules it programmes into the UPF.'),
 'UPF': ('UPF', 'User Plane Function',
   'The 5G core node that actually forwards user packets, applying the rules the SMF gives '
   'it and terminating GTP-U tunnels toward the RAN.'),
 'UDM': ('UDM', 'Unified Data Management',
   'The 5G subscriber data function — the successor in role to the HLR and HSS.'),
 'AUSF': ('AUSF', 'Authentication Server Function',
   'Performs subscriber authentication in the 5G core, working from credentials held by the '
   'UDM.'),
 'PCF': ('PCF', 'Policy Control Function',
   'Supplies policy and charging rules, including the QoS treatment a given flow should '
   'receive.'),
 'MME': ('MME', 'Mobility Management Entity',
   'The LTE control-plane node whose role is broadly taken over by the AMF in 5G.'),
 'PDU': ('PDU session', 'Protocol Data Unit session',
   'The logical connection between the device and the UPF that provides IP connectivity. '
   'Voice typically uses a session dedicated to IMS.'),
 'NAS': ('NAS', 'Non-Access Stratum',
   'Signalling that passes between the device and the core network (AMF), transparently '
   'through the base station — registration, authentication, session management.'),
 'RRC': ('RRC', 'Radio Resource Control',
   'The control protocol between the device and the base station, governing radio '
   'connection setup, measurement and release.'),
 'NGAP': ('NGAP', 'NG Application Protocol',
   'The control-plane protocol between the gNB and the AMF over the N2 interface.'),
 'SCTP': ('SCTP', 'Stream Control Transmission Protocol',
   'The reliable, multi-stream transport used to carry NGAP, chosen over TCP to avoid '
   'head-of-line blocking across independent signalling streams.'),
 'GTP-U': ('GTP-U', 'GPRS Tunnelling Protocol, User Plane',
   'The tunnelling protocol that carries subscriber IP packets between the RAN and the UPF. '
   'The outer header addresses network nodes; the subscriber\u2019s own IP packet rides inside.'),
 'TEID': ('TEID', 'Tunnel Endpoint Identifier',
   'The field in a GTP-U header that tells the receiving node which subscriber session a '
   'packet belongs to.'),
 'PFCP': ('PFCP', 'Packet Forwarding Control Protocol',
   'The protocol by which the SMF programmes forwarding and QoS rules into the UPF.'),
 'N2': ('N2 / N3', '',
   'The 5G interfaces between the gNB and the core: N2 carries control signalling to the '
   'AMF, N3 carries user-plane packets to the UPF.'),
 'PDCP': ('PDCP', 'Packet Data Convergence Protocol',
   'The radio-stack layer handling header compression, ciphering, integrity protection and '
   'in-order delivery.'),
 'RLC': ('RLC', 'Radio Link Control',
   'The layer that segments and reassembles data to fit radio transport blocks, and '
   'optionally retransmits lost segments.'),
 'MAC': ('MAC', 'Medium Access Control',
   'The radio layer that schedules transmissions, multiplexes logical channels and runs '
   'HARQ retransmissions. Unrelated to an Ethernet MAC address.'),
 'PHY': ('PHY', 'Physical layer',
   'The lowest radio layer: coding, modulation, mapping to resource elements and the actual '
   'radio transmission.'),
 'HARQ': ('HARQ', 'Hybrid Automatic Repeat Request',
   'Fast MAC-layer retransmission that combines new and previously received copies of a '
   'transport block.'),
 'OFDM': ('OFDM', 'Orthogonal Frequency-Division Multiplexing',
   'The modulation scheme underlying LTE and 5G NR, dividing the channel into many narrow '
   'orthogonal subcarriers.'),
 'QoS': ('QoS', 'Quality of Service',
   'Differentiated packet treatment. Voice is given a dedicated QoS flow with bounded delay '
   'and loss rather than competing with best-effort traffic.'),
 'QFI': ('QFI', 'QoS Flow Identifier',
   'The marker that tells the network which QoS treatment a given packet flow should get.'),

 # --- media & signals ------------------------------------------------------
 'EVS': ('EVS', 'Enhanced Voice Services',
   'A modern 3GPP speech codec supporting wideband and super-wideband audio; widely used '
   'for VoLTE and VoNR.'),
 'AMR': ('AMR / AMR-WB', 'Adaptive Multi-Rate (Wideband)',
   'The earlier 3GPP speech codec family, still used for interworking and fallback.'),
 'ADC': ('ADC / DAC', 'Analogue-to-digital / digital-to-analogue converter',
   'The components that turn the microphone signal into samples and samples back into an '
   'audible waveform.'),
 'RF': ('RF', 'Radio frequency',
   'The analogue radio signal that finally carries the encoded bits over the air.'),

 # --- computing analogies --------------------------------------------------
 'DNS': ('DNS', 'Domain Name System',
   'The internet\u2019s name-resolution system, used in this book as the closest analogy to '
   'telephone number analysis and routing databases.'),
 'IP': ('IP', 'Internet Protocol',
   'The packet-addressing and routing protocol. A device\u2019s IP address changes with '
   'attachment; the telephone number does not.'),
 'TCP': ('TCP', 'Transmission Control Protocol',
   'Reliable, ordered byte-stream transport. Too slow-recovering for real-time speech, '
   'which is why RTP runs over UDP.'),
 'UDP': ('UDP', 'User Datagram Protocol',
   'Connectionless transport with no retransmission — the right choice for media, where a '
   'late packet is worse than a lost one.'),
 'HTTP/2': ('HTTP/2', '',
   'The transport used between 5G core network functions in the service-based architecture, '
   'where interfaces are expressed as web-style APIs rather than telecom protocols.'),
}

# lower-case concept phrases, matched case-insensitively
CONCEPTS = {
 'number portability': ('Number portability', '',
   'The ability to keep a telephone number when changing operator. It severs the historical '
   'link between a number prefix and a serving network, and forces a database lookup into '
   'the routing path.'),
 'paging': ('Paging', '',
   'The procedure by which the network locates an idle device. It is broadcast only within '
   'the tracking area where the device was last known, not across the whole network.'),
 'tracking area': ('Tracking area', '',
   'A group of cells the network treats as one location unit. The device reports when it '
   'moves between tracking areas, which bounds the scope of paging.'),
 'handover': ('Handover', '',
   'Moving an active connection from one cell to another without dropping the session.'),
 'roaming': ('Roaming', '',
   'Using a visited operator\u2019s network while subscription data and authentication remain '
   'anchored at the home network.'),
 'jitter buffer': ('Jitter buffer', '',
   'A small receive-side buffer that absorbs variation in packet arrival time, trading a '
   'few tens of milliseconds of delay for smooth playback.'),
 'jitter': ('Jitter', '',
   'Variation in the arrival time of packets that were sent at a constant rate.'),
 'codec': ('Codec', '',
   'The algorithm that compresses speech for transmission and reconstructs it on receipt. '
   'Both ends must agree on one, which is what SDP negotiates.'),
 'circuit switching': ('Circuit switching', '',
   'Reserving a dedicated path for the duration of a call — the model of the historical '
   'telephone network.'),
 'packet switching': ('Packet switching', '',
   'Carrying data as independently forwarded packets sharing the same links, the model of '
   'IP and of all modern mobile networks.'),
 'control plane': ('Control plane', '',
   'The signalling that decides what should happen: who is calling whom, whether they are '
   'authorised, where the destination is, what resources are needed.'),
 'user plane': ('User plane', '',
   'The path that carries the actual traffic once the control plane has set it up. Also '
   'called the media or data plane.'),
 'encapsulation': ('Encapsulation', '',
   'Wrapping a complete packet inside another as payload, so each layer can be forwarded by '
   'nodes that need not understand the layers above it.'),
 'segmentation': ('Segmentation', '',
   'Splitting one unit of data into smaller pieces to fit a lower layer\u2019s transport '
   'size, then reassembling them at the far end.'),
 'exchange': ('Exchange', '',
   'A telephone switch serving a group of subscriber lines; historically the node that '
   'interpreted dialled digits as switching instructions.'),
 'strowger': ('Strowger switch', '',
   'The first widely deployed automatic telephone exchange, in which dial pulses drove '
   'electromechanical selectors directly — the origin of the number-as-instruction model.'),
 'trunk': ('Trunk', '',
   'A shared high-capacity link between exchanges, as distinct from the individual line to '
   'a subscriber.'),
 'toll-free': ('Toll-free number', '',
   'A number that resolves through a service database to a destination chosen by rule '
   'rather than mapping to any fixed line.'),
 'caller id': ('Caller ID', '',
   'Calling-party information delivered as signalling metadata alongside the call, not '
   'derived from the audio path.'),
 'esim': ('eSIM', '',
   'A SIM implemented as a reprogrammable embedded module, allowing a subscription to be '
   'provisioned without swapping a physical card.'),
 'sim': ('SIM / UICC', 'Subscriber Identity Module',
   'The secure element holding the subscription identity and the keys used to authenticate '
   'it. The card is the UICC; the SIM is the application running on it.'),
 'resource block': ('Resource block', '',
   'The smallest unit of radio spectrum and time the scheduler can allocate to a device.'),
}
