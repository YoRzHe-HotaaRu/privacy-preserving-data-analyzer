"""PII Detection Module - Custom Entity Recognizers"""

try:
    from presidio_analyzer import PatternRecognizer, Pattern
    PRESIDIO_AVAILABLE = True
except ImportError:
    PRESIDIO_AVAILABLE = False


class MedicalIDRecognizer:
    """Custom recognizer for medical IDs."""
    
    def __new__(cls):
        if not PRESIDIO_AVAILABLE:
            return None
        
        patterns = [
            Pattern(
                name='medical_id_pattern',
                regex=r'\b[A-Z]{2}\d{6}\b',
                score=0.9
            ),
            Pattern(
                name='medical_id_mrn_pattern',
                regex=r'\bMRN\d{8}\b',
                score=0.85
            ),
        ]
        return PatternRecognizer(
            supported_entity='MEDICAL_ID',
            patterns=patterns
        )


class EmployeeIDRecognizer:
    """Custom recognizer for employee IDs."""
    
    def __new__(cls):
        if not PRESIDIO_AVAILABLE:
            return None
        
        patterns = [
            Pattern(
                name='employee_id_pattern',
                regex=r'\bEMP\d{5}\b',
                score=0.95
            ),
            Pattern(
                name='employee_id_alt_pattern',
                regex=r'\bEID-\d{4}-\d{4}\b',
                score=0.9
            ),
        ]
        return PatternRecognizer(
            supported_entity='EMPLOYEE_ID',
            patterns=patterns
        )


class PassportRecognizer:
    """Custom recognizer for passport numbers."""
    
    def __new__(cls):
        if not PRESIDIO_AVAILABLE:
            return None
        
        patterns = [
            Pattern(
                name='passport_intl_pattern',
                regex=r'\b[A-Z]{2}\d{7}\b',
                score=0.8
            ),
        ]
        return PatternRecognizer(
            supported_entity='PASSPORT',
            patterns=patterns
        )


class BankAccountRecognizer:
    """Custom recognizer for bank account numbers."""
    
    def __new__(cls):
        if not PRESIDIO_AVAILABLE:
            return None
        
        patterns = [
            Pattern(
                name='bank_account_pattern',
                regex=r'\b\d{8,17}\b',
                score=0.5  # Low score - needs context
            ),
            Pattern(
                name='iban_pattern',
                regex=r'\b[A-Z]{2}\d{2}[A-Z0-9]{4,30}\b',
                score=0.8
            ),
        ]
        return PatternRecognizer(
            supported_entity='BANK_ACCOUNT',
            patterns=patterns,
            context=['account', 'bank', 'routing', 'iban']
        )


class DriverLicenseRecognizer:
    """Custom recognizer for driver's license numbers."""
    
    def __new__(cls):
        if not PRESIDIO_AVAILABLE:
            return None
        
        patterns = [
            Pattern(
                name='dl_pattern',
                regex=r'\b[A-Z]\d{7}\b',
                score=0.6
            ),
            Pattern(
                name='dl_pattern_2',
                regex=r'\b[A-Z]{2}\d{6}\b',
                score=0.6
            ),
        ]
        return PatternRecognizer(
            supported_entity='DRIVER_LICENSE',
            patterns=patterns,
            context=['license', 'driver', 'driving', 'dl']
        )


def register_custom_recognizers(analyzer):
    """
    Register custom recognizers with the analyzer.
    
    Args:
        analyzer: Presidio AnalyzerEngine instance
    """
    if not PRESIDIO_AVAILABLE:
        return
    
    recognizers = [
        MedicalIDRecognizer(),
        EmployeeIDRecognizer(),
        PassportRecognizer(),
        BankAccountRecognizer(),
        DriverLicenseRecognizer(),
    ]
    
    for recognizer in recognizers:
        if recognizer is not None:
            try:
                analyzer.registry.add_recognizer(recognizer)
            except Exception as e:
                print(f"Warning: Could not register recognizer: {e}")
