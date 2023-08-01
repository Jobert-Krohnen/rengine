import openai
import re
from reNgine.common_func import get_open_ai_key, extract_between
from reNgine.definitions import VULNERABILITY_DESCRIPTION_SYSTEM_MESSAGE

class GPTVulnerabilityReportGenerator:

	def __init__(self):
		self.api_key = get_open_ai_key()
		self.model_name = 'gpt-3.5-turbo'

	def get_vulnerabilty_description(self, description):
		"""Generate Vulnerabilty Description using GPT.

		Args:
			description (str): Vulnerabilty Description message to pass to GPT.

		Returns:
			(dict) of {
				'description': (str)
				'impact': (str),
				'remediation': (str),
				'references': (str)
			}
		"""
		if not self.api_key:
			return {
				'status': False,
				'error': 'No OpenAI keys provided.'
			}
		openai.api_key = self.api_key
		try:
			gpt_response = openai.ChatCompletion.create(
			model=self.model_name,
			messages=[
					{'role': 'system', 'content': VULNERABILITY_DESCRIPTION_SYSTEM_MESSAGE},
					{'role': 'user', 'content': description}
				]
			)

			response_content = gpt_response['choices'][0]['message']['content']

			vuln_description_pattern = re.compile(
				r"Vulnerability Description:(.*?)(?:\n\nImpact:|$)",
				re.DOTALL
			)
			impact_pattern = re.compile(
				r"Impact:(.*?)(?:\n\nRemediation:|$)",
				re.DOTALL
			)
			remediation_pattern = re.compile(
				r"Remediation:(.*?)(?:\n\nReferences:|$)",
				re.DOTALL
			)

			description_section = extract_between(response_content, vuln_description_pattern)
			impact_section = extract_between(response_content, impact_pattern)
			remediation_section = extract_between(response_content, remediation_pattern)

			print(response_content)

			references_start_index = response_content.find("References:")
			references_section = response_content[references_start_index + len("References:"):].strip()

			return {
				'status': True,
				'description': description_section,
				'impact': impact_section,
				'remediation': remediation_section,
				'references': references_section,
			}
		except Exception as e:
			return {
				'status': False,
				'error': str(e)
			}