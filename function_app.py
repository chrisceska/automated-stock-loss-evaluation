import azure.functions as func

from stockloss_demo_api.app import app


function_app = func.AsgiFunctionApp(app=app, http_auth_level=func.AuthLevel.FUNCTION)
