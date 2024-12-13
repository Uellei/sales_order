import asyncio
from flask import Flask, request, jsonify
from flask_restx import Api, Resource, Namespace
from bots.bot_manager import main

app = Flask(__name__)
api = Api(app, title="Bot Executor API", version="1.0", description="API to execute async bots")

bot_ns = Namespace("bot", description="Bot operations")

@bot_ns.route("/run")
class BotRun(Resource):
    def post(self):
        data = request.json
        bot_name = data.get("bot_name")
        if not bot_name:
            return jsonify({"message": "Bot name is required"}), 400
        
        # Use asyncio.run to execute the async function
        try:
            result = asyncio.run(main(bot_name))
        except Exception as e:
            return jsonify({"message": str(e)}), 500
        
        return jsonify(result)
    
api.add_namespace(bot_ns, path="/api/v1")

if __name__ == "__main__":
    app.run(debug=True)
