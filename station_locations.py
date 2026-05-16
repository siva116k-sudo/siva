# station_locations.py
# Dictionary of Indian railway station codes mapped to (latitude, longitude)

STATIONS = {
    # ── North India ───────────────────────────────────────────
    "NDLS": (28.6419, 77.2194),   # New Delhi
    "DLI":  (28.6558, 77.2309),   # Old Delhi
    "NZM":  (28.5921, 77.2509),   # Hazrat Nizamuddin
    "AGC":  (27.1767, 78.0081),   # Agra Cantt
    "AF":   (27.1800, 78.0200),   # Agra Fort
    "MTJ":  (27.4924, 77.6737),   # Mathura Junction
    "CNB":  (26.4499, 80.3319),   # Kanpur Central
    "LKO":  (26.8381, 80.9346),   # Lucknow
    "LJN":  (26.8467, 80.9462),   # Lucknow Junction (NER)
    "ALD":  (25.4358, 81.8463),   # Prayagraj (Allahabad)
    "BSB":  (25.3176, 82.9862),   # Varanasi
    "MUV":  (25.2800, 82.5600),   # Manduadih (Varanasi)
    "GKP":  (26.7606, 83.3732),   # Gorakhpur
    "FD":   (28.4089, 77.3178),   # Faridabad
    "GZB":  (28.6588, 77.4246),   # Ghaziabad
    "MB":   (28.9845, 77.7064),   # Moradabad
    "BE":   (29.9457, 77.5515),   # Bareilly
    "SRE":  (29.9678, 77.5497),   # Saharanpur
    "UMB":  (30.3752, 76.9237),   # Ambala Cantt
    "LDH":  (30.9010, 75.8573),   # Ludhiana
    "ASR":  (31.6340, 74.8723),   # Amritsar
    "JAT":  (32.7266, 74.8570),   # Jammu Tawi
    "CDG":  (30.6942, 76.7652),   # Chandigarh
    "PTK":  (30.3460, 76.3869),   # Patiala
    "HSR":  (29.1492, 75.7217),   # Hisar
    "ROK":  (29.6857, 76.9905),   # Rohtak
    "ANVT": (28.6300, 77.2100),   # Anand Vihar Terminal
    "DEE":  (28.6700, 77.2100),   # Delhi Sarai Rohilla

    # ── West India ────────────────────────────────────────────
    "BCT":  (18.9398, 72.8355),   # Mumbai Central
    "CSTM": (18.9402, 72.8356),   # Chhatrapati Shivaji Terminus
    "LTT":  (19.0664, 72.9089),   # Lokmanya Tilak Terminus
    "DR":   (18.9629, 72.8293),   # Dadar
    "TNA":  (19.1865, 72.9742),   # Thane
    "PUNE": (18.5284, 73.8742),   # Pune
    "NGP":  (21.1458, 79.0882),   # Nagpur
    "NED":  (17.9104, 77.3152),   # Nanded
    "AWB":  (17.6833, 76.8167),   # Aurangabad
    "ADI":  (23.0258, 72.5873),   # Ahmedabad
    "BRC":  (22.3072, 73.1812),   # Vadodara (Baroda)
    "ST":   (21.1702, 72.8311),   # Surat
    "BVI":  (19.4518, 72.7856),   # Virar
    "RJT":  (22.3039, 70.7337),   # Rajkot
    "BKN":  (28.0229, 73.3119),   # Bikaner
    "JP":   (26.9124, 75.7873),   # Jaipur
    "AII":  (26.4478, 74.6399),   # Ajmer
    "JU":   (26.2723, 73.0019),   # Jodhpur
    "UDZ":  (24.5854, 73.7125),   # Udaipur City
    "KOTA": (25.1803, 75.8359),   # Kota Junction
    "ABR":  (29.3600, 72.6700),   # Abu Road

    # ── South India ───────────────────────────────────────────
    "MAS":  (13.0827, 80.2707),   # Chennai Central
    "MS":   (13.0827, 80.2707),   # Chennai Central (alt code)
    "MSB":  (13.0810, 80.2785),   # Chennai Beach
    "TBM":  (12.9901, 80.2435),   # Tambaram
    "SBC":  (12.9774, 77.5695),   # Bengaluru (KSR)
    "YPR":  (13.0099, 77.5561),   # Yesvantpur
    "BNC":  (12.9833, 77.5833),   # Bangalore Cantt
    "HYB":  (17.3850, 78.4867),   # Hyderabad Deccan (Nampally)
    "SC":   (17.4399, 78.4983),   # Secunderabad
    "GTL":  (15.1667, 77.2000),   # Guntakal
    "GNT":  (16.3067, 80.4365),   # Guntur
    "BZA":  (16.5193, 80.6150),   # Vijayawada
    "VSKP": (17.6868, 83.2185),   # Visakhapatnam
    "TVC":  (8.4855,  76.9492),   # Thiruvananthapuram (Trivandrum)
    "ERS":  (9.9897,  76.2882),   # Ernakulam Junction (Kochi)
    "CLT":  (11.2588, 75.7804),   # Kozhikode (Calicut)
    "SRR":  (10.9890, 75.9472),   # Shoranur Junction
    "CBE":  (11.0168, 76.9558),   # Coimbatore
    "TPJ":  (10.7905, 78.8130),   # Tiruchirappalli (Trichy)
    "MDU":  (9.9252,  78.1198),   # Madurai
    "NCJ":  (8.7139,  77.7567),   # Nagercoil
    "ED":   (11.6500, 77.7167),   # Erode
    "SA":   (11.6643, 78.1460),   # Salem
    "MYS":  (12.2958, 76.6394),   # Mysuru (Mysore)
    "UBL":  (15.3647, 75.1240),   # Hubballi (Hubli)
    "BGM":  (15.8497, 74.4977),   # Belagavi (Belgaum)
    "GR":   (17.9833, 77.5167),   # Gulbarga (Kalaburagi)
    "PA":   (18.3957, 76.5614),   # Parabhani

    # ── East India ────────────────────────────────────────────
    "HWH":  (22.5839, 88.3425),   # Howrah
    "KOAA": (22.5626, 88.3496),   # Kolkata
    "SDAH": (22.5677, 88.3707),   # Sealdah
    "BBS":  (20.2644, 85.8358),   # Bhubaneswar
    "PURI": (19.8106, 85.8314),   # Puri
    "CTC":  (20.4625, 85.8830),   # Cuttack
    "VSKP": (17.6868, 83.2185),   # Visakhapatnam (also east)
    "RNC":  (23.3441, 85.3096),   # Ranchi
    "DHN":  (23.7957, 86.4304),   # Dhanbad
    "GAYA": (24.7914, 84.9994),   # Gaya
    "PNBE": (25.5941, 85.1376),   # Patna
    "MFP":  (26.1197, 85.3910),   # Muzaffarpur
    "BGP":  (25.2425, 86.9842),   # Bhagalpur
    "KIR":  (25.5500, 87.5667),   # Katihar
    "NJP":  (26.7040, 88.3629),   # New Jalpaiguri
    "GHY":  (26.1445, 91.7362),   # Guwahati
    "DBRG": (27.4728, 94.9120),   # Dibrugarh

    # ── Central India ─────────────────────────────────────────
    "BPL":  (23.2599, 77.4126),   # Bhopal
    "ET":   (23.1614, 77.9453),   # Itarsi
    "JBP":  (23.1815, 79.9864),   # Jabalpur
    "KOTA": (25.1803, 75.8359),   # Kota
    "GWL":  (26.2180, 78.1828),   # Gwalior
    "BIY":  (21.1938, 81.3509),   # Bilaspur
    "R":    (21.2379, 81.6337),   # Raipur
    "G":    (22.3144, 84.0542),   # Rourkela (Jharkhand/Odisha)
}
