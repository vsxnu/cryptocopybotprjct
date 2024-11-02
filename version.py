"""
Version information for the Solana Copy Trading Bot
"""

__version__ = '3.0.0'
__description__ = '''
Version 3.0.0 Changes:
- Enhanced configuration system with flexible environment variables
- Improved wallet discovery with configurable criteria
- Advanced trending pair detection
- Detailed research reports
- Rate limiting and monitoring controls
- Better error handling and logging
'''

__changelog__ = {
    '3.0.0': {
        'date': '2024-11-02',
        'changes': [
            'Enhanced configuration system with .env and JSON support',
            'Configurable trading pair criteria',
            'Adjustable wallet discovery parameters',
            'Improved trending pair detection',
            'Advanced wallet analysis metrics',
            'Detailed research reports',
            'Rate limiting and monitoring controls',
            'Better error handling and logging'
        ]
    },
    '2.0.0': {
        'date': '2024-10-15',
        'changes': [
            'Added wallet discovery feature',
            'Implemented trade monitoring',
            'Basic configuration system',
            'Initial reporting functionality'
        ]
    },
    '1.0.0': {
        'date': '2024-10-01',
        'changes': [
            'Initial release',
            'Basic trading functionality',
            'Simple wallet tracking'
        ]
    }
}
