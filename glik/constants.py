from enum import Enum

PAGE_SIZE_DEFAULT = 5

# Environment variables

class ENVIRONMENT_NAMES(Enum):
  LOCAL = 'local'
  CI = 'ci'
  PRODUCTION = 'production'

# Application constants

GROUPS = {
    'ADMIN': {
        'id': 1,
        'name': 'ADMIN',
    },
    'CUSTOMER': {
        'id': 2,
        'name': 'CUSTOMER',
    },
    'RIDER':{
        'id': 3,
        'name': 'RIDER',
    }
}

# User

USER_TYPES_OPTIONS = [('natural', 'Natural'), ('juridic', 'Juridic')]

# => User Document Types
DOCUMENT_TYPES = [ 'CI', 'RIF', 'PASSPORT', 'DRIVER_LICENSE', 'SERVICE_STATEMENT', 'RESIDENCE_PERMIT', 'BANK_ACCOUNT_STATEMENT', 'PAYROLL', 'COMMERCIAL_REGISTER', 'CONSTITUTIVE_DOCUMENT', 'OTHER' , 'WORK_STATEMENT']

# The users should have at least one element of each row
DOCUMENTS_NEEDED_FOR_PERSONAL_LEASE = [ ['CI', 'PASSPORT'], ['RIF'], ['SERVICE_STATEMENT', 'RESIDENCE_PERMIT'], ['WORK_STATEMENT'] ]
DOCUMENTS_NEEDED_FOR_JURIDIC_LEASE = [ ['COMMERCIAL_REGISTER', 'CONSTITUTIVE_DOCUMENT'], ['RIF'], ['CI'] ]

# Leases constants

LEASE_WEEKS_PERIODS = [ 12, 24, 36, 48 ]

LEASES_TYPES = [('lease', 'Lease'), ('purchase', 'Purchase')]

class LEASES_STATUS(Enum):
  PENDING_APPROVAL = 'PENDING_APPROVAL'
  ACTIVE = 'ACTIVE'
  REJECTED = 'REJECTED'
  CANCELED = 'CANCELED'
  FINISHED = 'FINISHED'

# Payments 

class PAYMENTS_STATUS(Enum):
  PENDING = 'PENDING'
  PAID = 'PAID'
  CANCELED = 'CANCELED'

# Strings for API responses

REQUEST_SUCCESSFUL = 'Request successful'
REQUEST_UNSUCCESSFUL = 'Request unsuccessful'
