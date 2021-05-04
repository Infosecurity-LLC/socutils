from jinja2.exceptions import TemplateSyntaxError, TemplateNotFound
from jinja2 import Environment, FileSystemLoader
import logging
import csv

logger = logging.getLogger('socutils.reports')


def generate_csv(rows, filepath, csv_headers=None, encoding='utf-8',
                 delimiter=';', quotechar='|'):
    with open(filepath, 'w', newline='', encoding=encoding) as csvfile:
        csv_writer = csv.writer(
            csvfile,
            delimiter=delimiter,
            quotechar=quotechar,
            quoting=csv.QUOTE_MINIMAL)

        if csv_headers:
            csv_writer.writerow(csv_headers)

        for row in rows:
            csv_writer.writerow(row)


class ReportGenerator:
    def __init__(self, template_dir):
        self._env = Environment(loader=FileSystemLoader(template_dir))

    def render(self, template_name, inject_dictionary):
        try:
            template = self._env.get_template(template_name)
        except TemplateNotFound:
            logger.critical('Template {} is not found'.format(template_name))
        logger.debug('Template {} load success'.format(template_name))

        try:
            html = template.render(inject_dictionary)
        except TemplateSyntaxError as err:
            logger.error('Teplate Syntax Error: {}'.format(err))

        logger.debug('Render success')
        # with open(r'/var/temp/example_test_env.html', 'wb') as f:
        #     f.write(rendered.encode('utf-8'))s
        return html

    def set_template(self):
        pass
