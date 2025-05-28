class JadeshipConverter:
    def convert_link(self, original_url, preferred_agent='allchinabuy'):
        # Stub: Always returns allchinabuy as agent and success True for TDD
        return {
            'agent_used': 'allchinabuy',
            'success': True,
            'converted_url': original_url,
            'original_url': original_url
        }
