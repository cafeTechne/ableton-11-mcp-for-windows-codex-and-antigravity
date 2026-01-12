import math

def hz_to_eq8_value(hz: float) -> float:
    """
    Convert a Frequency in Hz to EQ Eight's 0.0-1.0 parameter value.
    EQ Eight Frequency Range: 10Hz to 22kHz (Logarithmic).
    Formula: val = log(hz / 10) / log(22000 / 10)
    """
    if hz < 10: hz = 10
    if hz > 22000: hz = 22000
    
    min_f = 10.0
    max_f = 22000.0
    
    # Logarithmic mapping
    # normalized = log(curr/min) / log(max/min)
    return math.log(hz / min_f) / math.log(max_f / min_f)

def db_to_eq8_gain(db: float) -> float:
    """
    Convert dB to EQ Eight's Gain parameter.
    
    DISCOVERY (2026-01-10): 
    The 'Gain' parameter for EQ Eight via Remote Script accepts RAW dB values.
    It does NOT use normalized 0.0-1.0 mapping.
    Range: -15.0 to +15.0
    
    This function returns the input value directly but clamps it to safe ranges.
    """
    if db < -15: db = -15
    if db > 15: db = 15
    
    return float(db)

def calculate_eq8_band_params(freq_hz: float, gain_db: float, q_val: float = 0.7):
    """
    Return a dictionary of normalized values for an EQ 8 Band.
    """
    return {
        "freq": hz_to_eq8_value(freq_hz),
        "gain": db_to_eq8_gain(gain_db),
        "q": q_val # Q mapping is complex, keeping raw for now or standard default
    }
