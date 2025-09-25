class TemplateManager:
    def __init__(self):
        self.templates = {
            'Login Pages': [
                'site:{d} inurl:login',
                'site:{d} intitle:login',
                'site:{d} inurl:signin'
            ],
            'Documents': [
                'site:{d} ext:pdf',
                'site:{d} ext:docx',
                'site:{d} ext:xlsx'
            ],
            'Index Of': [
                'site:{d} intitle:"index of"'
            ]
        }

    def list_categories(self):
        return list(self.templates.keys())

    def get_templates(self, category):
        return self.templates.get(category, [])

    def add_category(self, category):
        if category not in self.templates:
            self.templates[category] = []

    def remove_category(self, category):
        if category in self.templates:
            del self.templates[category]

    def add_template(self, category, tpl):
        if category in self.templates:
            self.templates[category].append(tpl)

    def remove_template(self, category, idx):
        if category in self.templates and 0 <= idx < len(self.templates[category]):
            del self.templates[category][idx]
