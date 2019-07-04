
from big_vmatch.base_application import create_app

from big_vmatch.constant import ENVIRONMENT

application = create_app(ENVIRONMENT)

if __name__ == '__main__':
    if "prod" in ENVIRONMENT:
        application.run('0.0.0.0')
    else:
        application.run('0.0.0.0', port=5555, debug=True)
