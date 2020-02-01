from flask import Blueprint, render_template

layout_bp = Blueprint('layout', __name__)


@layout_bp.route('/')
def home():
    return render_template('index.html')
