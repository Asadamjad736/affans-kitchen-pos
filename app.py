"""
Affan's Kitchen - Professional POS System
----------------------------------------
Advanced restaurant POS with daily sales tracking, inventory management,
and professional receipt generation.
"""

import streamlit as st
from datetime import datetime, date, timedelta
import base64
import json
import pandas as pd
import plotly.express as px
from pathlib import Path

st.set_page_config(
    page_title="Affan's Kitchen - POS", 
    page_icon="🍲", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Logo embedded as base64
LOGO_BASE64 = (
    "iVBORw0KGgoAAAANSUhEUgAAASwAAAEgCAYAAAAOv04OAAEAAElEQVR42uydd7xcVfX2v2ufMzO356b3hBQIvYVO6E2aiCIoTRBFBAEVUBFRQLCggEhRqqB0EKT3EnoLnSSEVNKTm9xeZuacvd4/9j5n5qYA+nuFBO/+fK7Be+fOzD2zz7PXetazniWqqvSsntWzetZasEzPJehZPatn9QBWz+pZPatn9QBWz+pZPasHsHpWz+pZPasHsHpWz+pZPev/r4I9l6BnLU1LUVABUBCQpuei9KyeCKtnrYFgpRaLgBWIaah1PBelZ/UAVs9ac+Jb3f5PDLRWbU4+BJ2+GvP7P2zclp6L0rN6UkLP6l0/iKyG61P/gX1tJxptxYhQIAf7fBLpqvcgI90P6Fk9kNWzelYhMjBLBqK/vYPCr95H2opUJiA1QKcCFh19LLWbH6Z6LkrP6gGsntW7MtuqYiQmcs8fKTx1I7p4LREMVLAGTEUwVjARko1PQc4pKVn0rJ6L1rN6AGvLrISsSOFPHYSuPwEjMVIZUAWc4KpqTEy42dFITZ8erupZPYDVs7ZApgVqxUy09Ofog2chhQwqTg0oAqIRSB4kBATiIWTPx3sAq2f1RgnrEYwFTWPYU05Gpz+GiBOrCjSMgKHQFCBiIYVy2Vd7XKye1QNYW2ALFg1FhPrOL2GmP4CpjH0mVUgZR5yAGmDE2euqwNggbo8Nlmft8i1oq2Hv/i1hZ8yZOtd8+O5D2HcfIiyMEiygMW4lCtKjg0QGWsh4Ki4W7RwSZuBKbI7nqOoi2CJv+9TplI7YH+0YgUYNvXVYNjCoIDW9CTc/CPKcT1LTuyyLSQMjcTiHRAjWtYIxR10lRwnt4QvL1P0bxVawcK0H3YIp2BwQyLpVkN1pI4V3J1oMmCuxV7/ca0Ow1Yv7SAWshVgVMOIlF5hLAOv/QLAgs5J3sWf9G21IQP0csY8+mb3ntuiUSUj1CGLW1eH4oKugEUKlKYJCtdbRIwPCYkAAhBCBCKTBu9LxGmCqsftfwLq/vMFzQA9dJkB1CfuHh7AL30RrUj5VzojAAO6/q7g9D8FsucrIE5k8fIMKdiJc8Z7Ci2DLz6KFJYguKbmeRRF6cPzBhJvvjRTaCQKWrKJf9NupR2SHLZPZIBDhNjBwVBNIqtmFvqIRwKieVdUxcdk/wI1+d3nV2TkTtX9+mLh+LqWVq80Ah8S1wWkWiE0O+52JX+1LZFBGqBleWyLz11ITh3/wVWTBqyhVMKqoOepqMFRbtMcjaI67CKk9fMtim+BYZeBJbOWpEKI1B4VZBT9+O8yZgKQDAj8qCgeiP3uw+7XvzbcSUL1XpICaNFK7E2L10X/yqgRUHcP87H70X1eD7v+f76YdrGVC5UwJi6U2wO4XDhK1grT4E1KqqkiU2nysKrlspXNAUERlfaXr9RKiQr1o3UadLB+oQui6xXo36QUtU7SLMV7hCK2HIBqVnCwSmyEmCiTVRzaLWdTlwCLxT3zZAl6rUBJoQ42y62mIkrYXS8+ZvD1AGmWLFhMkAfWC0sUW+vZAibh3P6R79Fg7pV4VuySXJsGSh7fOgK4cIkhcGjRcOggZ/31kox2hS1EZTnX5HVh8n90+6NAOqyHcO9T6VJzWPuOQaRdj/3UH2v92GLA8hxYhphA5WjMJGX4E0utjKyLSuL/BRK0E5Vi11Rp6Wc1afbMxVgoMpJWN21VKJHVzMY0vYq3PSouL2a0LyiysUQp1PXILAJMpep7akj/LXrgj1nxlaTwxjbK9wBdPRLvvhG7/CaKfbL4+qNYN2LLr9myoI1BhZKF3dmUvVQmV80hWPyOBBKQ7NmV+6K5g3IlPLdnP/WtDBstV9oVnRUGkZRsYsDUyfaJ7Jp3DGBEwCk6YIQcp1oyGklS5+1wAU/J/7Oc32AqFh9/cRXR2DPSRSxATwMTqVk9Pj7h+W27GWlvyM3yfRRtvM7gTZ+PXPq4gM8xYCHweSAOqei4BRzP0m4L0GP/X+3dNSQE6YhPoi52LjgyDIAVtqMEu7ASlgjUCg2D6aZgDJmPlr3A1u7rqruZSUG2r3ULdVOseD6VrWcLqy2nLCjmrbOjBSE5NvCqTBywPJNGWbWjLAgdgZArhnueQcO9ZG59nZ8+1/QgbLZ50OXj1G+Tb/4k99dDSm4lJgbNkzmmue/KJ2KH9yR77G7LhVh8n/4Fw7rE4T1K9j3D87m1oowTmgJ2xr/1ng8xUIRhBdqWPMfgzV+GH6+JSCfWlQKEDbXJ9mn6EHTzNuxcGzcZxlgMR0NwS/3QFZdxGx9+IZFr/hs51Q58lU/HQa1tTnnQEW/oypuhSiW0C1A3AnXY7ZouPVtX6q9W/5y6R62YilS3P5iK7X0N+ox8RXbRmeS3SCVTMjz1eY/Cu7rQ/B9t9Cyp9Qf/qZ2QbbKsrA38BmGUSCLbcAWzL4bh7z8MuXLTmWcg/HB19bO/96r4HErbc2X+nC2GX3ovWCw+7Dgl4kK1cA0Xw1a7bGxU9F70MQq91sLG/JJ57A4FZ+aIOMIaqFw6dFWbWmTj1WNHTYk4lWLHDk8+uG4q++C8kG6z3E66v5wv9jl52FbYhBwd8m3A58d21hPbiRGJPr3bbCvu8A67c9/+AYCPXVraVlJ6nYVdcR2FhWY5kQKDXolYtyRLc8zdIpuOV4jKwiLhIYfHjnP40sWMmWB1MJiLcaybsjDd3sBbdiln+BPFUX9I1dNZO5eKzL/geu+/9yL81G1vnoLrmQqRyYgk2PwUbDyLCeFvHqt+XgJTyKxNlSYrSdbQKGHY9heZJ/vW2ogKt3BYz8hwkrPbGquX8dPOfCH7+VHweUOgAFULYxZ9LtZ4fRlBvqRZkCmh/9D7Cz77jnHQ3/S5Tz94pB5nCkgOVY76MxDCeYfCde0LM/hoMF1w5xrJq1dL3IgZ99eayVdd+C9S7VdYh1dpjqG+P3JcugREH+DCoLOcjP5Hz4AMh2P2bUFqEFFwJO2LUmWJZvDNl9PNVCsc43iZSzgVqrrCvMrX1oBcX4QOqjmdHAaO/XENYZd3Jslf4dJbWw2M3IQ09kQlno2P3R1u2QZpGwMF7M0XraMYY6tx11/yf9fwzCv//sHRKGzrnJfSVWaAe8X7//bALJ6D3jqITzyx3/68l6dIilwz1h1JdL6KNTrCG9ucoSxBGiEagk5zWIFUvQbeFUdD6XrjzX3grqqRVtAgafh9tHwmFfghGYMRtTFEhyiJz3wWzqZYXJf5dGzVU9YyFpDpRfVdw0p3A6xKj/VcYjqSC/uCX5K/5ESVRSg2QIF1l9xPquJ9i+g7+C4u6onm8iqCq0d2PwPz3DmydD/Pnp6CNQdG41NuU+2/HTp2A5BUz8rgyC7liMck1jch1eFLhXbJp2nA7NzBD9gJFMEVdMpVc2Y6uUZkqNOrCTaVqwmFUtB5l1X6/8QnaMxgpOk/GGGa1sGRAa0JIFAYV/YvPEpeWU17o0NwFTcXuWbWrxA6+FBNkq1mBVnED9XhUBqssPrFTHwjdmmKXLK7Y0UX74QUyTQrdyLDRxUiyoWI0HmBIGYvOBcD0x5hBjhoS9HfFbQIC6+gwacj4LgLGfbSXEZ6vCNvNQca3Kt0T5wVYcBMMGIZox9/WKpLpSl3Y9tsItzwK/fgeXKJdV1s3dfaVvLOg3nCqAH28wLfBS+VAK3pC6uxkQ2V7jPypx0MpQxTH2KVLyq6Xr2SDEpLsQth3PCv3uME7t95/LfqsHqKcZgXbUA+LLsd+/Sp2cUDZtl2M/fsf0P4jYJtvwepXsG0bCj1DfYlftQhV11OjtaBG0Gzhjisugb7jEA0dQhYgme+SNWvddfGeVbPHSDcC6Rrg30tlO5YIF52LzRcR4wJ4USFZ1E4cnE8w6yV03ngobS+IlhZvVHmCLsS9+5KJd8Yc+03/lgSy5F8+S2k2GiVp1CvgQly2zW4YfPq58RrP3sfB4xY2mWZ0dAl8rSyY9y/mnq+x7rTDwjmbjHw/JOc4sWWfxVTVbxR3Iu3bQ/oMhVkPS+d85I8HIXV9PQgrd8e4KGspf2p/jHn+USzQ1Gd9KrNyni6zpy4TMEtkxbKqZaeBSU1hYQykPMrVkETbHIDHfk4J7xQU1JdXR35+nlKGmt7IbSDT68p9tw99FdK1fLv1nZ/juPUiZNARVbg7skhE4dmrCY0gCGT08bDd9wBylcBg06nE9/8nMp2bVEKvdREs8iANnixc+B/ie3+OtpVQn78P4Sp+BXvEJuRxjwZqumagXEWnXb+CsCyfGFaQvB+c83Xsmn8TT7wU2eVsVCo3Kjdz6S+xTQtREae+1h/7qc3L9+azc1VhxHSCcTcgNX1BgthnD3v32Yh14oU6r1LUFtx9HnHB//GJ3j4TWhTpPB47cAxP3v03/nzRr3n2ppuJxG8+EKt7kHRaQ1zs7gZb5cYVp/EY9vV/oY2LsemAYlFp71Qm7r0D1A/ENeaROG8S0rmqtmimP5qEXYvRe3SAFT9/B7q0oix2LeqN3J1j9XH3m9T3RQ/YDamfCP21NE9W4DMDay29TgA0OaDPj1j9y/m7VTrhuvyxe3z2HleZ++SA4oPnoC1TvYMo6qSjhsHoBhOR6s8S0eTDMHdfjMx43SfDExS7fPJc4LTU74YMTsBq9wUvToOUeGYLsXPfRGoHdEsJ+wEfxU77+Z//iDCfJxthKBmBzz8lMAKV3pECmWJMqeCFKRc+i/3+B4kCB/gw3XU+AMkMV2ccu89+BLNfYf4fj6Nu+NOs/v77WEEzEXqPQAyP4tz92G1HE0z4BuR+n3bQMQYYsD12++8Sj7+FoKg03vQ3tHNv1K8bPZKSJ4majBuzr4c8L8Hr1iSSy3Bk1tBE1CS2stBiBWWezA6Bkd/BrPJqEUMb1zzjGzkNtKqZ6u0g6+uG8U3p2m25EVVcO90B6P91zuwjo07ASwH8uVNKGSWBaDf58g2keqB/45qit8+9MpsVONX1QL2x/8dY8A/M1GnYZln9kbdZEnx1o/kxIZIwxdfOwe53MfSTf9jzFqBGN2y2j2i//T7s2K8RDh0MeM1WVYgRXwQkyMwbY/Pz0Y61+CAGfwkbl9w92fFQzC/PQEVp6PRgrzr9+5v4Lwn3M8YKDEb6lA2PqKH6oQ7CgFgMpjAQVmZ+ce5vfK6jBB2jMG1zSEqAtu5CssfxVFr/Cpu5FFsfC8XGWdX1GmEDg0QCkgyoLuD2mIY0foT9y8/w80nCKhQFEpXyNTLHSK0BOz2kMjKYCKqZhmzbPpj2f5DkOM8D4HhTHnBbHj3iPtkR2yGt4Xp7VBXR/QOMPDcZGbfjKtdEWU+ZxSlnNZUPP4wM/QsM/4u7bA0bAO0B9vPfIfDQG6PgwSyKw3TXSbAE9lHfaztzgXVWHmH7wY2rB/vSUPmh6ngOWH5xplU8ITlBEWrP/7bf5b5qonf3VVhH3xEn8PGPHeA24/D1q64xIHCJLgU2IuP2w64uS9rH4okq5VsmRipbY3a9bjUL7B+7dH1nd5SAbgYahngyvoB2ToWmP4OOuR2UYPDu2IEH+NCAqJizhXcD2vnwaFJPLx6U9ax1zX5N8/r2WH7rrZBGmBShQCljIKAsKVIYCHW1bixueA0amAq3A1eRyFivFhFJYVh2Erb/FrA1fd/pc31XzHwXaakvUI8RlHvxvzEpyMhJMBh6TXcbovq6su3LIdJ4UF1nDGZP4CUTZ7qB6Yg0wUFMxE7ZzDfKOQFVv1OPXx3VK3FQXgrm5PV5dr0uVt0W72FAtkAnJQvnU/w/PiJQABJQhKQHZvjXYYtzsRdfjP3nq2jM2t4IF3BTIM+AHQLZ5gCk4ePqPZPtZ2HGbgXSbY+CMuiiCTw+7jNKz3woNb3XTC5s2/vLQEEgI2/UaPZalapk4fVcQOqxm4vMfe5ftC9Z4oWChcJ2WzPp+BOZeepJhL3q0JJSdybSUldg2+ehjXPRfDvW5gmd9w+47zLspV9kww3XVfID0ucT2C13I5jwa/TbP0Vj/6pdVnR0MTLjJ8h3/4bs/XnniXceT7Tf6Yh1FYgxVYqgkjWe54xIgkD2/ggd9XWQMPEfULFYBUt+bdKP9sD++hL0wSspNJfB1RCBnC28/fOf8fEL/8cKN8PHGOwYwzil6qH/UcMkTpKb1L9n7Rc76fA4hIZVfwkILk3T+nUBhJc1RZ0Yr0R9Hep7cR/+vO58i2InXcVUg7CaIKqWbHyz9BkVVWc3JZWYIuIO9CnTV4c45eB2N6TPEERndV0ct7rcV03AnD6R/Ht3EwI4RkUp3z8Qc8AV5GfMJH/N3zH6JZzuPxdZ9G+UkMOWlJx1mRXkI2/iLRfDM/9Fdty/DN3rZLTQANgU9g+3sMvsTzAn7Uv+yh9gL/wS2itm7UEae5PDEiTqjz3tcoJjzsDqyh4YX7Tpa7PJAKWjEY1qR9CgoPzW2TDMfQKz97VoY3nqo2uic8QnHakO+6sW6P/xf/PUz4+nECuRZbDkGI7Yf08++atfIbtWm1EFdRSuCgECiJ3eQWkcdN53jvCuaekigujj9y/tQQDkbv8vTfdfg9T2h2HjJIPzJ5DZ+uupvA25HZdmIJIqU45F5ZR6DbKxS7cSIXNWZvE1PIYh6DMSs8+PoT5XuRATLw+6WpLqCQZ8mfj3q9EIpGEqZvIdmLq+CXvSCuR/1xkkhy2RvyifQHf+3sHqbrjscfe6BvYH6soM5qZPkmUzUYaUJISmCaOc71G5C1aM7FqQpe+Bmh2hNldmQ8IEbP93cvl0JFsuiRnXAcfWl+PqjH2bboI6q0XQU/W4qufeC7Pj5yu99dZdpf36Bc31Vfbbl0DDYKyFbMaP9HQd3yJQVpStxS98kCCqI3TPy9jBP8Jse3JF9idUSM6z71mamI6P/0Jn3YgF0r/cH2UXcPJP9cL+Z3/gwSt+Tf3cFwCIfA3j5J1GstvwwaxduWIjuLClXbfQQiufZqE1lFwlTb16Nq33mKoSS0GTSgHRiKB5W2yD7YyWwH1/0H8Psa4tA9AE2GxP7MCtsUoyNQ9eiY0KEBiMWCJJSVq23n6CojVT6kVcBn2Hrln2uA2+Aw9SK6+xTb+H9J/w9Fm28CK+ahhSCpFMoZz3XZ0bIULH4d+LCLecAq+8iI1SpcAK2shjX/1r/vb4k9A4vxJNcUczWyj1d/ESDBJIZ6T+arVem1U+u8T9VFXGz0vAIPl2pEUcKyMDoL4PZtSHE6C4MSnb19WTrGp6rBek3HIdZkzZy5x/HlQui3XNZ1yNnD5G9szDYckcAwqWkEACwuGTGXLeBeQBiWF1kUn+5jPI3/YXAk8TtQKBSVOBMS5HmyK15ftdywKJoaFgMAiaE9I2F5KKipLb5sNr7a4P9BqN2edMr9/b+Z3PztZnPRi7HmBo3wTvOQcW/5G3aBtI6mHc1V09qA10j/99pryYQKIgZ+6Pf0eIgIFrRImLziWrGffRREzJdSPfyedDTZ1r39fcnsj8AZh+Q/yEyYfZ2IHINl9x32cV6/5BmYGLH1fuC/j7gsW6hUii0RTWn42z/YGL0+UcR23KS5+x/oGHyT/5OCYEHSUCF7zQ6suB9v+GXbZ4xXcV7Q1tORLLtdTFe5K9fkI1j7lVhSizw42LEg1eB3//OJJODRSomOkIkgFjB1UCiIqArX6IAca7goJxOcRFBL1kMpJtZwXa7p3ux8pBp2G2OtRrZfsw5ZmvYcP0yGkniZBoRkk4YKhziRsbRbvPxeif/xflDq9JqgFzVTqjjAw8HrPVV5A+oyDf5ZOoGrPwdfTPP8SC0xKRKJKY6EfijAhQziP7fI3b9iTPWBMvjNWI8JJDcaqkvGpaHDoSN/5r7iLYuM2JWDvFmznsmauIH76NxUtWjzrEza2cP/coDpk5iwMfeMA7Lf49uvcUegt7f5tw3G80NGh7EBhDYAQtRFAoVSlVBzIIAEdR3AhP42RoaFKmHFJzIfbyH6CidK/GgUwngBT2PAte59ZzWxysUxJWSi2cC8+cm3BhE7+tiLq+rjLdvhXSb1uYONd1Z0yL2HIKrsA7/fgTYBsoLXKcXukNJLr25t0x9BxKLmR7/hiAC01TENp7hOJBX5JMIcS2+7zrfv/VZWGjYvXXIs2cPx6CXUeX+3YWc+ApSIetCWLQbU9AjzuUoFgvzvvsXI9Qn6Elk06p2RJNeLAI+05Df+r3axsAteWYhv4PPMDklSsoPXUjS2f9i4a5s7GFeF0NEtXWjKLWtSCdpxoBSuulxNrz6gWrQaU4BHLZoLx9t61u84N/IEw77Zyb4Fk3YRfcR2iMVzhFbLS1SxDqdSskgxZ7uQGpKq8Cj/ag3rHHyzl7x/5c8cXdeebMkylK5eAyaNdmhpaHXnddN6DLxYgyk4pFmLAUuExsW+8JSmIX1NW3UlUKrLyY/dY1ty++HywD55uW1gspUzISfYyO3NvH6wS3L1NXvPJBPl5/g7pMffSYcmxXCtgJr66MTFw9Sl+rW1GqG/R1qK81y3QFW1iudEs67SdftL4nRjLl4JZ/J6znK9SXMFFV5+y/K7L/sb4jE6MT7yT/1B3YbQ6tULbqCyv12V6o7lPRFqzJd2M6q51a2jQJqosWocIJPc39pnGdgfS77i2s9oU9yJ4vD5jqJf43Y58+UwIzuD4oR31dJcFEBDwMvjzzpOAl11ZVk2qEOGtMSeMkEAGpYDH5n/4YqRm6xgALG1+OZYv9aHkicVnf00IhM3acRz+bg2tPISm/fxQ58PNEpRYVlSRWyyYaxl7hktWid0zct+u6cyKALMhYH8BqNUSMLp+BJB01tzsq7Rwq6Tb2pSsvu8H57uuXqGm2KsL1yrvWSLN1PmEDJ9IXXuiPJ4Bc9K7bNf6U+r1//W4id4tY/fG7vr/1z7L67Vetgb2+2rO63AupH10VpVg7bKXS4y9Y77VS92FNRQDkBdkXvytLw8mHnsF2dbX0+8FD2PkCHxEdR48hrMlANoeN0uf00UowGxtZcPaPyIai5SwhWq6V/cUFBzLSTvJrtESk9J1ckLW3lq0u//40P4GNNsK5trPvcKJvj2e+xEdaHcBGApqhT3/QGGRQuc9gJm6HaHPFqjIuhT+3Cj6chWQq+QHq8uVJ6K+BuYjmg4VdtlDq3dHFF6uGipSqvx8lcOqKeZLtx+RCSkCA3OEHEhjpjNCqujmN49qClR2PruaZrnWmNghRIeia4n7aQhuznnsO6iXqTsLQR6cTz32HbMu8Sp+vvjdKsV7q7nPVfkPVnrvfdffC0ktPhVQ9FYYvJkNFfUWQjNrRe0Dp3l7VyKJ+oqSvqYV1R8YvKipLSaV1Kb/til/8kvjDD5JgSmkQEqkrooUC+kubY/fd05FIi8AtpulTv0TwwoNbVgigbRoSsWGykUim02e+FJVC/OYdFKNip4/qH81FhGL9Qil9qkvWVbvQlRZ1nXlN9cp9Lz5cJ1jVj1f7d+U2r7y9DZugQvvkY7dPVNVu8EAlL79KINZ3ufR16h9LKg6iT+7j32zAoiR/ri53iCgmgZ7/K3TBMxgDtuCByo++1CFx/g++hLr2BY5WQaUaPJ0K7Jhaf9wrpvu1uvsROxz2P8Ti3uXHmZ9XrSGRfJjENOteQc0mof0UX/ffxL7+ZIlC2mQMtjtIPrGg8RqSVhYlECCH/Re47Ty1q8v3WUwnjC9B4ezvuijH7h2EqpRq87JvOq3d2DdV1yg4/TNHB3TgcPKDy5aRBDqLSfq2SK41+Wq8/pzjY8PGxL/7FbRl3KJXdV7pXa66K4VK5iLSmVft9qW7YAv+5i+YWK02VygfJ2DFxeIDtzOzn6F9cMWzOvs3tHMrLw22f4nvfARyyH7E7/w/Mm1LMEk1P4Xh9q46lcln2lV1Cck0lzHjD0DH77oyR7hcPLK+sY4QqnfDXdf9P2cfp2BJi1qB7XcazLp/BRMfKkti7PZ6BTuy7lDx5qLKorjPKfz9FyXEALY7CeMzcL9z91GfvMZkA78GYrrcbHGxr7hiX68ydO+eQC+5jzAxM+uWk6uWzI6rAVS1ZcvxBCWTXwWusiyRTR1XwYEX+JfVnXOpP8b1jItUvj63SjfHj0mUWCUL4AqsBk6H+skJp7B1nfS0y1G8bI22C4s/4wK8DqcYuw2y+1lIkl4PYNWzTLDC1O3dgMyu3yIqWVgRjPycXLyglmthZeU6XNW/gCBHMPqH0FamfehJ7veHQ2JZ7lV0fhzZ8wvQ1s+BCUF0UXmXy2p1lQ4gs2V5P7eB4wR0rUDy7ZD9sAN9j4r+T2nK0f6Iig22xR5+CAxQH7S5KoI1yC4/gzY/pZ+sfTgqk9DPVwRXbEmFQl1VjShO3v7CFM8m39n5qCQokjyAkkw1h5rEn8P+57suZ/KpTRwBK21f8hxaTMwZ9ZbPJ4v8muHFL0wHIHxYMMll0u7le5bMFVEx8eTf9dITqizcB9e6PrG7pq/KfRWVkhDvV+2da9mlO6vo0xZRBaCrJqw+Pbzq9QlUuWdDd1jftnVdWx0BFCdP7ib/9LmlfSTjGcR4DakKyf53ztFhIqPJ3XUh4Z+y4DLYBi5fNF2F1uzB5WGSrSTgprXbVJgxG5pulQR9VthbXWHrj2mabn0H01Uf7pOGvOQ1mHdLAokQ7roi7LgjsPlF4NWYzX0Ntvji2uv8i3rYwp4/F7Ht2OQ9y2a9QOHFPyX6jG7/5zuvUfl5B4itMEbY+jClIroGHa0IfV+4nujFp/3NMyAsd0pGztx0g7Wj9pAmzK7g77MscK7Bql89QHfFozHw/L3eYokl3HwC29q4Wp+4T92tWTrYdFVQd9GvipRTU6/c1dSPXv+fVKNTf/Slm8B66s3/kabBGs/R2rD87RmkpL5Svnyz9L9dtaP1IAnA7KzA2KLOepfCrEXmlykHrTrlvU4TVIe11VVPkfWHVOu75KtMxdITN/f8OSV/EW0/i+mIZryZNWAhV3IZ9qRjvMnyv6PSd8TVbr2Ck0SRdmt6loQeFb1JjV3i68tKuK4Xl+7G/eSAbVhP+wC5izfE9NWLJilgbSt+BVta5MZ31bYdH1N1U3yGqM7PvRGNWfO+qz1D1cTDrbLOo8Is6nsK7X9E/t4/klVwoxV8It7lJ0j4CT+tysb41bM1ZnxckdIPN8MeY15Vu8qJ7UwKk6A6CUFZc3A1fH0uVnV8OgF2j6+w/J8nQa84B8h9NkL+6UNKgaSqvl8YsED7GjFFpFtPyp2tm1pLZapLk8JqQ1m1t7vyccvVdSvuPhn23d3lIn6sHzc/x3gPqrMbfn0nvNukqv1+G1crQxrLkVj1/T5L7f2zvk5e6dFp1SNZXQ3Tkk7Bjsi/zs1lQy0rN7Uc93GR+qeQxv5YbROSe8IrrFSvyX+B57J8XGC5neQVZ3qtyA7ELj9wE/LJJK53x+uSbgIr2q/JVgpUN+aKK1OejffRwH2+jqjKLFU3VteuKz1nXUte0mM2+QmWm26RiiH6yWux9t5K4a05brNnwlKpX9LvcqY/EyQli0PwlrKc3HTdnXJ69JvxX81ry7eawHUQm63Fztv62qLb7F3e4Pm9M9l0FrSPzzbBJsE9+yn05pxZ9z2s8l9S1VW6Ps+KvlwH/J3Z1LsG10OSuhv89TifqlZnuu6PPK2cVKpb+abnTukvvlBQwt4n7Nr9dxr0hxDUO6nFb2OyPmGWXIsD0i1/qP9SdxP4irZ68BKM35t1D9lv+svq9ySBkOAYJ1F8/BSEAjZJ0lMSypD4qPpKX3edqvuuO8KSSHyrb0t48rqlo9i4uOr5q3hSyyJBiPWvwrYtLpftqJ3pz9ryQ5QZKSVcSRxrQygySWDceSi5VU56qsQ1FT63gei9NWX8XXWG5KZq89aNvD7Xhq4V6LbQ7SUK67LOoqp5VqfdvKJY3m8p1THujvL+5YstqnAswl9+7esZfN+tPnTXp1rrD7n6OmkF7rldsujN9rXb9T6sjpNo+kXmDn30L7CtM9cqV8VrST+VqjVRAsYkcDmNa/LwZfU2Hw4kuBmPJQK3jVBt1SHQidZxP2z+e7tCeBJl7Wr74qcdgO1qKq3/VfULr2Hz07B9xqBv6j2/DZVbf/nZsxQff9LHiXVTbU2hWta/iG7PysVr8cBpeV2M87nNr5Xo63sqItkAbL4dOqaXpENox1K0cTaapGGtz5XVrmQjz3K4zKxd4n7P1Zps0l39AEEh8rVHmN7dm22L2m1/CkXbJx6tZJbV1erjHmT1QV/9Gso0z7s9jRfR2L0txvU93MslXbMHSy0Y0n3Hk7V19pPftqqf8LKHMnfb+X6YF8eutEqwSdOc42hGkW6Lz0lAZO3fQqN2SD6tJkqRqO2LHHw67iWupx2LKVhIvoCCMRCDDdS9TEkFbOFYj7x81/0NqruP1ZRZtc5K+Z1D6mhgs6/XhqI1Llc9fnDfL63qVQ7kvh+nd72qMqCVn1mC6fMrwvCMv69+f6tPm62vzZucQxLvsW6aVQfTWzdrF9kX/0mllw5/ByunfUs/O+HgyI6u3JXhTbAwXrSSwQ3LqhwvzbJ7aUKpU9KL7lKuvAVwHWRoXidqmhC4r7evfLlvvUX3Oh8z8mZY5a8LJ8jXJiEabtFJufafPbr1GRqx/YjX7V0lUu6sT/BuaeC8u/eXXPNSuPIa5t5h3bgTp4+pT7sT31vv7UX3m8m8SWDZUQmttcU+O/8OY0oHw7gtLT7nrrE4gQ7mUCn8FXYNUm1nKb/DH8f3sxzFMFiwUgrjt0nS4f6zNUvCwDh1jYL1FXk/AZHd76HAGH2NN9z9G1ciB9NlhO2L0PjTVT7PJz/6vj9QaZHG5NcRQ6bK64oVCOfNXqqbS4bRZzt0T7O3q2bbjsH0Hue/d3A1mRB/CMEASFaKy4+pPZ5q2FvHT+qjMB/vjdx7DfSbuHnmOmrw1X6LcXz2fpOKlI6p1zLxk5DmG4IznQ+oVfIB8m4ca5M9E4POY6izGrf8jZLfcb9xVRhZq7pV2tFMMOjsQLBxH0l3RyAHAF1FfaJ6pPphLxP0Xf04nK1FcMpgxldtrPmJ8uMq3TyP2uJY6yNEy9NidDdJ6yN8sSrbw4euVfuJSSaY0PLc0HhPRP3R56a7bMpJv+17I6vGcwCuPkP04QwvtzGOrcHqTv7CfiVDMwwVH/Pk12xHzUCt33zMhNfUMC92aJ/fq3ff4CmsuM+qP/jag+vdl9L9aK4vnrr7sTq4TphUj0X3e8d/Zg3PXrjtQMzt5xGmBtLsX8kQfYI98XugfZfz79lqCk+hnxqqq1OUuP2k9yp5Criuz58ITXsSCddzLySsd3pNFg5wJwJvA/h65Y4Kcqqg9qrpRtdhcVd3NUPWT66tzQAez35q8CojlFZ4ytX78i5VbZSuqkX+1zu7Pmh1LwYYI8kPe2Y8P6MsrDfE4V6xOSB0bQycP/t8OKV5O+FptH1L8Xg5VClGRYMnIL2LLs8nS/SOJM+s9+6ifvKSlDmQqorjWLcHjGg3A7WphG3YbD1M3xEbrzGx7wMQSkbSlOBFz5CY/5Pj8OEkKfowYrvtr5Nyw9jNOMiVb/y8M2AEOeo1FofV89K6x3J71spu3evi29fq4O/faebm8vS7MV8nBfTX1/dKcXpq5aTzndA7rQ24A5qX01MXu/58r9yGwni3Kl7kPtyrddP/vmrPVOqKfhbrN19PWW35zLseJzsbDVVWwWq6C1+PRlDv36tnQ1Wzgm5/pw5snG/7enXNshvFv/OmRwLXjmCCVSGTOkTL1uZ9DbC6C9R9v7l3VfJblKrbdLde6t/TrzN1cF/XVqOVu6vSqksMyaI7fOqTM9T9mP3qUqL+2lcH1q7YpF0K6+6x61SdK0A9GqW72/nN7a4xL+EFvTofsxpUbeIYrbzrPXQ03SE3DrYmpU1F8YdVvld/kH4tdh2Xtu/rde/lW3dbqL9O5tVdK87i6gJzRaXcq+vXNW7h6mtWHdPqO1yRolotk8T2+st+MzXG6rOlnZ2h+jG/9rNiM2hQd/d83tPdRfdc6Tks7v0EBBnuWXqjJLMu0TbWT2Wc0USuQq/19qLSq7LcJdDl1tbd4er96lBw9cyuTXv1PYVr3sv6Y27Jz4wqcSSoC4nC8fZyx9L9GegnqrqL1Zdx7yqCKDVdYV3fJhJ1tnqPq1n8lbq06h3a3UG7h1g9B1FXfVjJQsoCqEqNWFSM+lWxwDozdrsDuPYB/K1WzWEqLtSrEDi9yyKfWlfLKdQy3sGvq0Pc19F1LlFWf3rLr9ZfumLiqqOmL/8Hrm/1lZR1z2P1g+++oHq8udA1KGZdD0sbsxqu5H+TohBSvr/7gOrReF/Ri/FFHtyx09/8tZKg5V0ptbSX7pwll+lVmTIfgqmfT68b6m5AVQr3coqL/5/8/5pHVZL6B1A/6jG6XaMrrVQ5mVcDx1VMJ+usKjDXz7T1Qbj6+VU/R6uvLlox7KshCev3bd09H9+gYnN6S95q9+XNG16fOq2s0/V4fVc40V3dfSqPCPb8hE1/jvXVkPc02C41rPpe6tYNidcd3e7O+lpWZqvOsdG0PqVf1wGq2qvrWlyVKfA3avX7WtOZ6z4ut2bj1V/ByrOoXhy/N7j/r6vK2bzIefWw1TWYrT40Z/6U2epgbpKCuGmx/5au/5piQqpcvm4f9KqGvbo1w+oB9fS9Wmt4GOHvpNs9fBIr67PcIq0+1rVoaTf/yo2vN7G6OZNcGf+qqc7s2n/EvkYxw3eDq6JdiRbVbK1WyrJaiiIhVbqg7lSpq/tKqL6vV1d66n4G3YgCVPYsqrXTuJs2b/KtdrXUKhK56gM3L0asLr1yP7Drw81/HmU+Ur0KZfUAuS7Vz0Jlsrv8KxbvKt/4Y2C3UFHdH1Vp8TehS19nQG4Df66L/krQxrRkS+U6iW++/vO8FWDpP9eS0nVw+QJ/1VXx1dYd6n+39rD6jR/PkLu1DxWY0UW+9lt61KuyLfuYb7Bne6Mpo1qjz2RF4V1Ll9p+5f62odxPwPhaMiWZ5BqT49dmGfP/cvNrFZlb4aiprLneuvP63aY1qKt9bVeC5oPn+fpKSS5mFd3Bu2Rz+Crb1YGlenjprp1lDea6h1WtqVwFvl23Nf3X6JfVbjbsjXrfXL9hnJSC23zuRzxHqq4/0QoP2hN4dWSSKz2O6H8nGcFNIJ++4ru7L5DHdV+Zil9e5GmDpSOKL8krL+py7K4UeHf8h7W9H1sKkdVYYJveE6Bm8joL0Fc8cB8LSaK0bsRr8dLb/tv45dvlUueFVYy9t1mK9YVbwMbdoy8XQ74Esu9puO4YtzbTAggqVJdlMPK7sM2tsPEBiN9ZWAeSu3eOGwNs8ztMhS18Y2iGynfOc8PWNENHPzQxKdAfQaMSolG6OBfRtRfjr1fY5Rx1yXcC7P4jzP4nEZhZvlN4U0o1uTlaAzfnrYulRrjzaOzcc7FXXIk2z0XjTgK7PkbUYjNGTjD4L6cgm02nYn2UdbE9smR7xBjtC3Rb95mpJhcyJpHTEMKiG3bU/1Os/fKx6N+PoHjuvmgH7c1sfCw77bITf7zxRlLYys7j/i7SlaIoz7cR2v/HpBsuR9uWIomjIUDTAYgR0Pc8BQ3GkJ3r3jf6GJ1uSgtvW+6ydeT33IwwsFAFBlWXDAkGyYYwpj1m+31R09X5p0rR1t3nycEXE+52OKGbUv9ZR0J1OdbR/TYxUUCrQQh2PxqdaEhd/0BQ1tMkqjqoI78B2zeLCeIkp2pRDGQ8uWgw2lKRW2nQ5lQsydv30mPz32C4F6HhA38P1W5ZZJxqCuvRfn2U3Zav9Jh9rcWO2mBZW66qHbrpAPdErgx8RRD0H07Yuy8SVb+ZRMK3pP+Wol+tJ0/30N05/Xx2X71iX2fVbqWonjNcezDv7u7X3y1d8xcP1s31dHPv3SJaR1Mr74UCE6nJkEOz2w7I3niG5k3JSu1U81J/PpOsuWpDSLydcOOrtCumrI1uUeLEdCjB/zsIxUe2FkI9h2qN7cA2QmAi2PZbSC7nCyFWQ3/Rt1X7QLpx65w08R3h5bBJD7eC11P11+Z1FVX1nHS/9sUWCm1VYxZ6MFbLEo++Fk15qXYx1d29XhU47t4TV+u+rZ68dX0xLmP0sua4Z03a2ck1aDzL3T5/r4sua23J+3Vk0K9iA6s2T8+8s4Uli1GzEvWh1f6I5Uet5cC+d1jS98rR1/bcmv6yb8VYrklN6C4kI8HyA/TVSoStthB3nL3xJqD+6b1Qz5HrCtbkmBvqv+7O2p22rjs9vrtutxpgCfjMGDXl4+9a76JqPzdxDOu3pveT9lE3+cK6bl1Ufj+8ch21Wl1J3dWp1RPB6uZ6tj06Q1f36uuDVa8HuQGc7+4Zu/1d7T1Uf4+kHmJX/PeuPmP21XFMP2e6k4FbzWD5p5gs6W7M1d91vaymHYicRUXK7C2boUPlG1v3S6w//qQb+7poe5CqrfdbpsHr1WzvZsfU/v1u9m2P+1fd+7Nm8Otq2Kr7S1j1+3V/Zrbl7KPaOIZ1vYhRuec1BTGskv3ZnNgyqI8x3XCg1S/lxbLk4j56i0y3cF5VdpS/wO6rKmnc9vnf/K7Tah6b37/ra5Hq1nH1I14rAVzXz03HZt3T9pWObkQzu13P1qxBXwq3I9YfzmZ5UmWtlJRqqT6++jhF1/tt3FgI1HULlVp0//Wv06reDcHqF1f3S1yM1OJjP0tc+RpO4kT9udR9FnXTSFfYbhJNpWp7uRZYFld8qstzVj3L0pRz9YbxhP31jFau5dMhR3OveUx/9Vd/Hizd+n7h+FyO4CthuS+6dJkSB3rTvKdNyZ9KioR4IVhP5rnpbL1+G+CHxL81SssVgq6TV6wD/A11Wunq/ib0O3P/DRdrWj+VoLYGrHPLPSoP5v4fCwHYhFVnfdBne3TZTZ1s/Y82pz9zI/6P9WE3Rb82ml+1DcLafk1RrF2/BZ8kXv7MqIpdVn0IG+Z+1Sdvdw8wNrGLaFIXZf1x25+zfPfvtvtaXbwUic1+3u+L3N52uu8AbKkLuWbntwuxuO4tLxv/AXj2+o7zCJbvVH83fPwX/oNXq/++gSnO6g9zo+psFqseYGLjJZGrf9KS9/Dm6X6rnUQ1DdUGOR5V34Nu0p7apO7x3b1J1l52rEu21Z3q9Or9LTG3elW9hkg1odFHqdrVk7LX+1H1NOGmHmNmUwFoCxxId/2VrZ7VYGMgV/UmCdbSPVxd4OkkQVb9pKprrbueS7cB1+2iK2POxqQ86spq/H6nIG3JINrFxOruxr4pwUffNVAs9yJuoFvR+O6PlQCt63M3cD2rLwbtNmxXD/Jtcp2D99Lp2oKBdz1rX03Rr89C+4wNrXX1q54g3urW7M1iV2+SrODPRPsgW1sVb9fO0+oH2t2I1uW4t0hltb7d80Ux7yov4Y0RtTere1b7pr7GsVvcyopJPLrqKLr+Ld6Erbt7aDKmvak+zLOkP+J63phCQduadWbX45N1J9I1lPV3VVVCv/5h+pG5ukT+zRre+qa3UuZ0zdx1eXF1mWQ54yD1k6oWuLGpIF1WhrE10UzW2x7RW7fQ0T1LZtvQzby2yTpyXaXF6u+SrK5t+P7fvH6rtQLiWvyz7jo0lVq9vvJbV/Ouy1yryvLWrZpyF6u8l/VPL9b6ntfnufNtDb65Bqtxk3UBle0U3XWcrh1drk6rJEGrBpuu5IRrGWj1R1gZ5JwVF25TdVjSXcg/sXIb8+3Nfc5eJzHd3fPNXIlVrNb6X1H1S9e/R51NEPd59Fz20uOMuv7sxWcmfJKT1FUg7i28Ru/5H6o2rnmN5lqE7u51PVhVj0F3gtnuyau6q0Kv03rrG3+rM99vnQfmJ/PZVC3SzRu9Xo6sW3u6WpO66ueUlwTW5pQdpdZ91A2Nad2V9FVmXTVv21i9ha66mbq7TnXjlh4A6L/bGjfKncQ4OaJ44IYlJtff9l9lJOu7G7sJxF19eT01j7/nk6r7Z3NkSF+baxNab1TLcXTrRKw2QrvrJpWqfl6Y1b4n1v9uyrWWHnB3Zcs+jL6r+rBm3aH7D1qCZ4t0c/eVyKfbfaR8RV+1Ppmt38P0xR18LSs/L11VxRUPl67Bcf2V9VbMWW9d8crqKNfdtzQ1s7M0tmSqbwV7WP3jzzr+W/d9rBd1nyrJ5LXQ/aF1zSiXjPH/08KqN3tWRP8sd9ZXeJp6o79qsrmbbzyeX9eT2KqT0mYCsjUFGqvcL9O1acdfK//C6K5xveEdAnTD5K3p1ttLyn57sEGb9Hx20fFZDg3K+mFdeze5gKALf9rUu33T37c31qLc1BjgEnfJVdP9xJsvB7gLSX0NqT0bjPs3ntiU0oQkRzFwv/dHw1J/QVW0Pr8/K4qIdUld6BpP9T0O1QlE/7C71qmpr+ZcUSCwi/5U/0l3twM3v7uDk7ol4go/QTofuO6Uf5Jb0e2QsfWzX62+PKhL/mtH86Rc9eFdFXG7v4dduy81O7tAbG/P6hRzX6C+d/B6O1DrZ+AsBbHyk9cHueqxrXy/6xK6XRCXzyqjKw2h6/Pq5k5q7z5b24Bsarprfbw/SRL1dybTqBpUtua2K5tB89DY9Qvd6A+IfHhJ0hOniSTad6rtiS3v6e65rLwZt/iV6vvqbPev4YFk9QOuHlqX2dfgO6nqbHh1i4M1B0v+76yx8fpagwB9r7ZAv5CXLv2grrthzbuRu9/T+L0s3TrE/d5nbLzaBEsoW+y+K/4hOeP4KfUaF7JgZ6yvSfHkEa7GidXVnyq9jN46zRl0N/iuRqh3tvTFqXhZz/P1QruCJuv3FfNkS4iuvqG8+li4Nmzd6eM2dyFLp7BCG3uCLUYqESKYVMTA8nT18X+3XJaaW1DnK1YS/hW0rDg/PTHWx5hbc/fF5n6o1XtKd8/BmwnHnLwREJ16u/hs7eKrDuG66I+0WbI96zrvK9TefFhfUqm2fBbb55PWl4J+qmX+vxrN0vUJZbd0bwXo2mB9FJhY/Vd1NOsgVn2+7jSv1j5DSoW7rIGQ1qH9E0p77RuYtSHS2K/RuR6s6q8yN5rX7mp7x1v8j4o+TNcQYjsPWru5gJgNGrCbVvOyswOUNkB+yz3UJipgO1CM6ApdU6uNU1bCBrv2+v+3e+6uO1XTxsd7TYXXq7FZp+dUdw9mnkfB4lLg/1bZfB03O+dN1jHtLgBp22KPo3LZP0x0M75Vg6vKivXnUJPMc0k7ZqOu9wYpR5sPItu1x/7sqxHUNrLZ7TzrTbwT/wPc/+bD9rA2Qp2vaP3fC4NVodfAfVyXS4jLm+3em+3m2q1goLZzB/9Tlze5ZRkRrlxZkez6Ggs5Z7JBrDSV9WtrCqJbA/e3JPVHwtE7XvQsGkt1MWY3Pc40k2l3F5yzHpC7wExv1L1WC1BVcO7WLG3m3ep6f1eFTO5P2xK5xOvNXbISmMQVfdXrcmduv5PmSviS9Tv91j/O1T0rP5vAKiDqvmfFJsUJqQL3Ygps+kKuzcI06XoDazrHm/VM3AiW0rLGsXrBbz9TVpe9GXXnWMH6yMbfcG+YrjdCwK7S+LKv9Kq8H93U9K0aKlLX6NuyRL2/gxK/LbWtM0D9aekkf1HfdO1PFrAKUY3JsEixzI66YIGvWZx9LpZd2iF6l9A2uBrRlVOh8iTte6xWwzoUjNf2Egeg1hJ/YhHRIbC6dPXWkwllsnPG3vxYdP++xblUtmH3pMSRNDlrs7N79Yk1XSo1uVvVHoy+lgd3B2bxLoy92rzjQK7pMm7mJuyie+taN0uWPlhLuwd2bVKdLfXG2Q/r7lb1uPpWVQUcXvymy/1Vff51UJS1Xkti6xLQutM9rVk/yV/jtcgK7gP1V9gNcEWCqQaKNWuPbubKTwYBU/l/uQcXqpVrTtXyJkS3t80WcLt+7nXQ4LVKJqYrsq/uJrhH8vHvps4nUtnO1nDRNw5s69ET0B3kktVUtYfQRpXc5cbLxLpL7/QXrvs/qi6q6Hr4bs1qUZ3S/DvVYfXq60/Ue1Td7avkM/kad1XrT04snraWQvHre+/dv3cO1G/ahtsXq/I4pDTcCgB0Nxddh+ULYLyJ2FL8/elUuKRdSBIuBxN9BpK/fS425RulSjqN6wG1F65fMr/a4nkTFlj3mb7+zO7qaVpP9lvls5VwktoA9Z3MWh2Kd4u9rYvT/kYIzVuvP4k0v19JpWV17evVrwq7qQDX7V9/7mELsK/+hS0Zt7dlhd81x2nKx8W6d1h9Qkyed//79Uu5jI2AtnvP0msAtH4gS5XMn1tLm7KB3iF04YxKkZZNmp1N9fKphnU+HnHj4nr31ZqDt03c43f9m8nU5LtBJsJN3i7OUOnnjEtS8d/ZpB5O4hK/g6txlD8ys67I9nWv9LaZ4/RmxR3UB+Z6Hnn3Ir9dAKyA4Ouf/ro6N6WRQ1dcJIGdfmpQq25HFVWPaF2DrGg7RrQd4zoYG48RcQHnRZfu1Qhx4P2vy9+17T5CbcU6ot2HL6e7CFucjOQn6MKOuAs+F/UZPj7vM8y50JcLQXr9WNUPqO3g9jfuwtnYlkUIEBZ8JcC0F2v9k5SlYmVpP6smzq5P7q2i6RLLF6TjYP3jttNhcQ46FyJG/ARpB4tBYl9t0cnd5vauqPWR9Vt93Hpf39emcp/evPZg1bOWKzvf+tSO9qmiOoiRfa/U7Wn90F95P/sE2Oq1SXJdzNqmQFdA1eZIFawWoWjU2Cmr94oSJKr2tdt3CvUDTbS0SEVcNpmLtWJn9BfvOQm37rda2i7m1jvM4lRaG5DU3bi5k8ZK3WExRkssSbRKSWJQ9Fg6VYEQr4spK4RQ8gSxyxotz/W1YtIJMISp6wgKraXoYdQih3yL8gS8tmKTWIoakxpLIK4dVwAwFIZTKEwbWV63E55rLrAQYnbfo7zGawGCkkCG7E4HsI9f7O/Rm5MYRIGK1x01xKqECWTCQZCTMq8sKUu6NpGad38rXv/igOh7D0t2yW7OkY0V0X0KuvD6pZqlFaecVIXUbwVJTrcPDsp9RFR8hQKhRIbfg0b3mcYt+O80ICKSkgBLop2ELrxHOyrfrQrDxqHciATYWIy/pgVIIS+ieD0S/CsCK6BKBCJhYt+4f9cCV1RVGhypl0L14yCJRZPauYkoMTH+0rsSiqKxklAgxGqIBFYTKGj4fSQSIBRDEWcSo5zk2Uhc1mI0QCP1aCFA4yL4si5WA1Sg2A/nAYw4fU5XhZmcVyYl3jCxcqyx0RJiJAUmdIjhOtpZ1y9y/fJ15X9OABaJu1QeE7tWg++KEZx0QLwMstPqSF0Mq6T4iCcrsIhWWhMWsRix7nYFjLhPSuqgQVSrHJJGIPjHYnqNxFCMiT/2bVKjHdSHlnCAUoPtsa+nPG52/QHJqQbD7zAIFRGHJMFoXMGJW0nL4mgVvx9igwYw/lxdcPqFdRqxr4JShS7TpTyOenGxNF7uo5fTq3SgyjddJcSfoJIF5c6vZ0Z9CJt4smyyBv/3K8D1PzuJEgBNj0EiLkqEWE3qWbCo0XJpK3HxNn79pB8pUZcOZHVH9B80PJYSLqmKdTmeTvbBStDkEeLBatQmXeNJgZR41CUIXQcOxqJ10q0h6hiVEi4q9YhiEtoqUFHC1YGiTqxpSxYxWq7Eoc8nOCXjolZcAyxrfayNShuRlDyD7vWRpCxVi2qZUSPJOSmBWKvibHqBxIVilA0S/7LENlHrrjWma96T/1VQJbs3Hm7vj8HEzS6YKiH04gJGKZ0j1o12rF3zWc/WAYB3PkSuBbBSVblFzL1EwUqUunLrFZeUOZ7J6SWLceKoRkqgLnKtTioLgQjIm0QoEjfxuxGCWMEYsWBdi1NhjNbqBINsOT83iZeVAP2nH9fXbZ1V42wVdIZMqR1J7AJdt7zqQJESlQZFUXPjpY8LIYhYv0+6PmZGYjQ1zrqEGMMmFc59PyL8+HbS6plnUhTQrE8ZWUG8xoj8mkVVTyEgeTQpz3lFISJqxaOV65yaSLIuRlPiuQ/CMnK0rvCzD+JScpPix3hQrUBRKigQU0BVojRVWhOsuo9LvyeAFYRKSD4te5joFknEM7v2LBEQMc7qEYkRa51LEEa9K2I0u98lMKgyId2h1FntLgKq9o3j9k9F1bs+avIutwLQqA9h0+ZZQl01pd5IjiUkhsjVjrOA57IIWHKjG3f/Oza1c/+/BpCQuETJs8hJX7TEIq7EpGqJomKpY7nBkqCEMkDXXn4P3K1EYhDvIiSbgTjvXPDy3bRbkZ7VFArGaaGA4BRVk0eSUt44sVIdCrVbVv3eYtf90iR1LTcH3b5+5UBTrCri0+OScR7m+5h24Fy8oyMJvzvB5g2/NPqAuAiPzFeIKQet2jfLCQJXylLUIJBAxHpPLPCqNVbnr71amW0zP4hsySP9uu3P3u+UqMfgRvvT9xHlb7tbfv5V0g1QmhZfxDp1S3EOC6xXEYiTfnRAi8YRAUqijjVzB3RvWYwhFoua0E3qBCQEsEK8bBkYilF1QOSaBbnk1rmaVn1x0P+oSgy4yZVMHIKWtq3uP3KbhxjfBmRKLBYxRdrGCNaov/0SI2K80Uvl2kp1y4odCvFcJiWgxeWcBILTxS0l80Q8wSMrrtRORfkkBMqCi8hKb3dN7H0X2zJwK5Xe7RBTJQJ9/PECUgH8YjPqAEQkGVuAhLJKBKETtGBUS7DkFYo/dldfqisS9T8m9XhJ0z/07qOADzVTDrQkSLT9E1jvIhHnYSCGiJSOqQUXxLjNrH9zST8v6V0/F23F5WT4TEVKCxqL+6wUk/H1PgyI9x/9/SWJ1nXRNHFwWAnIyuvgIuD/UpnY+lGuebC6C5HU1bwkliB5+1Yy2rm+xJZxLvFOpPG/RkwpOB2g1AtKlS0rG+gW52h3kfE5TTCQQsQalPAXiXONmPLaSBLv6GLLyB5hJIRYBXGkftJarLilIbFOogVjylyXCPDGW+LOH3EUcb6If4WCFm6DqAOH0ThtnLvHpCyV58A0GWKpB0xTmvljbfsU8hzKCeoI1pStPVPHM7zG1eDJBgFiBA3VgVOtCHM++RTxdP7ltUULXi/CmHqXZwkSQBn+BPfGSCK7hN85iRO16ldE4V5ifMF6GZZE3PGlhBf+W4pIt5hX0yWOqN4RVu1qVtMBNe/PiFPeB/HhUXUZvKioi5F3P+QykOSydl3ll8KzI1R9a1aS6wWIwUYR0WtzCcyi+xl1VaHrqgSuIh1iiMH1r1pA0EV1gBrZQOeBxWONpTwEl/di08I1/0qw1h98d/EtDlC7WODdzNZG7JzX0PIeWPX7Tj6grdTiQdrjU3hJt2OjTtSFbRr6+2qkzwhfH1VKrs9YfLqO0i+8+wYk//+w/NxLEtSit2oT9RqmBevK0bRdYbuJR1LunhL3yH+RQwO1Ctw8x5M32nWxLkSL0i7hsk66o14IxRJHrCu3UcSJoCbBthKbFheY6HofXLT4PkKxRBSiBFg/xuok9CQh6rEbu/NZcQ2PamzJeU41WYsN/KHp/p8r9/UPQcUS1IY4yzzFMMsB2ZV/kiRVLjmuJYBFWmU+jVYEeO7StkGjTucKSoirjYGTI1hwO8YgWoAVL38FmPv7T4WLEd9VqlH3szfKq3e4JtMhKl58UQSEqOVREUjR3bKXJol6+TZrEAlRcXp0gbiUWkutD2k1akWk/qiQrPEEhD2k5JmYLp6NEuZ8JJt8/j/uFz/4nlc0CZI7oWUYFEsR0qzUJIt7/akShIV4BEeUc4q2zN9YSaNvVZ7EJMvLp2KM61kFF4VFxUdaiaBKiFSlmWQ8c6KrpTkCT1pUxUCkx9iyEN0k+33t/SmJWMG47l3Pie1w5CVCUlzh/rL6xTi9iPFM7VJGL2xS50wSj9fUa2X88xLBRm7NEf/3AIPqSTJJOlu6VieEsW4J+LYl/7c4oLKUCAvScCxkRVFSvk6K+mfjdDCzAnhCEkCzkl6BdUtyF7dWesUEwdK7UvVc/XK3LtI1akqsaeYucvJpL5TpPwP1MkTd6kmuF8l9SqqkO+85JS8vYUpBdxnIbfkHcYLMVbqne3u85O4i4TkFkC9bWJ57ScWfJJJwI7r+NjUvMFL+/pR5RvHX/7X4FgCPc5GPVBPrJfmUBUge5PL3pORjKbLPNzG6C8XqU/Z2UF+UUrpCb7Iglc45m+zPktiBkhGpnsPk3ih5UzS+Lp+fSC5/CSkXuKq0V5UCRRcoQaiz8JIIqf6jVwmZ7er9+/d0IdVUkxIxTVK/OL2A1OAhOSlEX6SUAGv6J1IffJ0Q8eKzMa6pR7W4WTKBqq8tWYZXOk71q8Yafb00Tj2YXpYhyTVCpAdGSn8rFa9byvOSRSpnJuB4LSX/BM1eSCGR8pYkCX93Uo9+7z9lD6vq0rguJmDpGJxOqNQhghFDShIVYVGP17iU1rIGSm5WiAucuwqVvj4h6cnCl9yK5PHqgKxUXjFZ2l5ElCKx61VVwYr+U3Hckn86Ks3xTVEfYOnKnKjk39CkHm4RUS0hSDDUIhuDFKHobBAy/8UWf5S2iLgXqyQrjCtiTpI1skRM2d1OgEuVZiGxLq5nWqMSIez3H9K+f8j4zSSh7qvUMGORhGP3RrfRSs6lsq6+C57s9yuXfIri96LkVYVt8QVJvW4xKjC+au3jf78KWW2lM0ncH+Pm1KiLc5tVb0pAAERkyT+59Z1P+TlXe1eSQXJ1+lKkP9SEt7zsnfnkImj3v5VWvqCSiRyEJrSfFS/UnHSXWEOVgsm8KqH2H4m7CkQjT/ZyIK4ySapAKQkrf/4mKfnq+SQk4OsZVSroBYE/8XJwO7/f4hdNtwJZtCxpfmSP8NlOonpV5v8I18sKz9+IL7Tw53OfhhBXgFgckEpK8lWUskGWsC6Kyl95m6PUIp7zueIeVYCVhltVQerG9tAkGZU+HyRj6iMrfwbJ85LK/SvxxF3V5yKVYlaNkj5NZYrL4rJ1nM2L/k9KCQ2jL3w2ovV++sE7flwW0VKF/H1VJbLMr0p11Z4KoeRDRlBWWcBWNgr9FPuP3h8lOZBTsnB9pGqRouQrmbyvOqgkv5U8FylhqUz+ilakbOqbTyI09UVMsUzFvBZ8qKS9r0ghsVBvtCS1eL1HgwP71fZQynkr1RWfWp/yYavmOCuApx6s1tk6qwhSLTmX5H4l9+unTymBUnXFI1BZmFaRrFz0GSBjp8LrEYKEl1X26CreW4Uf5rNUvGXGicRFKCEgAqJpQUypiNBIsl7Wi0nW5pJMzLeulDdejMR1MUk6pO6T/BZSgSVG8rZTCixSElLlC4NS8ZRU4W2T+0scwCb/VIGvJEtlWUdeIlZynhIzFjPkR1Ja8JxkpQAa15iBPM9TnnGHUuafuO0vKUnO1UjUfJBOSBQ2y0+Btv6U/HNluUXTpVx1XpO+idIFB3z9f5Jf8HrJ0sBAafmHqTf3Y2b/Z8XOJ85rMiYiUn9+xTtVqlalS9chGRitXJuaL6T+hyfkD9TbJas5W9rJJ/sHhZVPJ/0nJVWlWImcZJ2EYl0r8GRcJAZrQCv3mqTbdPs6K2zVVJ1L8anThRsrUtdbqqQj9mZJMm/SLbF+Gfx1KtP9iuuLln9a+sUq7FNC8l/Lk+RLKWeuOjOc1Oulz3iiyuzrFVbWCizt7M1vlBLbrZ2iSpvKzr+itmRzvsy3au1Q1zQv3xepDqPgr+5rCeDkUuIu2ZzZRHzZt/hGXAVQ1D3LZNoVEhD5kkvAag0++ddi1B+ZVjr7Vv8KpVIFs0uCOQ5S0g9LyU+aKbmFlIKPOna3lKd4g2Xde8Y8SrhFqwATj4W08o11cR5trLs7T7ry1ThdS6lcwNefZ3K+k1HKi9dJ2Re0F4/hvrcG9T4a6e6aLvlbWjSryW/OKtcKXH+3CZVvGkkP4GqVXVhW3T1Jxk4q1zCtvEgqPzsmY5Kcm5QmQcvXm9qvSTlnKZUp/7tI5YfaPW8+iULyOxWwFlfUaf3lSvkeVz59UqBe1hQpl8/7HXORqLRjWvHAPa9KPBX1oR0/tdwFsvCMJDFEUvFdLb1Xkn6nmdyTlCvsjSVQ6SkvWrG4xKlzi5c3lbNpCT5EfV61P/Z1zhVe+U7a5pXyXSYV3bTFi1jHXp1iTpPekUp7uVJElTty0pXQxrAt8k2p0Px+LPn0NdwF8bWeV9bzWSOmkXoPHa8yUVL6D62b/46XH9dNoVqYjGmF9ZkqqpRCWr9H8bTmeVZ7jPXnmW+jhI5LlUwVueRPuPQ0S2uw8jP/4or3lHwHq7fZSq+5P5Z2t6zSLCH5bVkmbFmSaVjM9PuXlGBU8l4rKSo/nfqCwHqQT+X8xXXUat9n+VhVQJSMvRQrW1q2JynlvsP7u78qX6+3pZLFXu51V5bK6/RL76I8v7LQJk8P1V2+m/2eRpKqP+nsV6zsy6h7Lpn3Mj1TvaUc/9q/RzK/5e3ofDK6LsGt3hC3ymblakmrz6Vd8hTW23pcX21mJIBoGc5N/VxKGzTPi2g+6Z/vy2a1vH91Jmhzbffm9+x/xVmpasW1zktOqbo4VY2q63ef9TtNsqg2x8PatH1O4uKml76FcbU2W9Rck7W1i51N+5s1qQm+FeuHbtEeTzYhJt9NP3BXr6h+yLXa1/Uzsc7XotnMpp5Gv/tdCJXT3HZ9lQpKj6PLWz+9Hdz8s3yP0l0HQdeivWb+ev2Qom90On5PT1h/AACu/KzqA9bPzHpbcPWzv7VmQtdniWxUxWmV40lK+Kjef3Lvq4x9rdFa/UOunhyvxaKsP+7bM52P1S7tyl3YhP2u6T7r+0q3w1U1KdI9MtiGpXzv/lGpGla9K1iF7N0ewpuxAPtGzG/nOJeN15q3scb9+cfz9d4J5yuLkFk3FduajGxJ+3bJmq17Sf1Zt8On78ZmfhcVgUyM76BWvv+6IqjYxOPpzrperP5nVUd8qepRT7eWimxxf8JNAjupAi9rDeJ2L8RZ0z1V1+LtoizSxjL1k/8PX8PqgSDVbrshdVXue1cqC6nCNnsb5cZe1y0KqP+cADiQsmCzrgIP9b1PO0+yzQeHTRIR3Kwf1IvFrwOopTacdd1X3+zjdXvOV2cP2pQMsav3tFmPWBvFmq3cO/LG8/xaaCKh9aFsBYHdRpqGma4D+s5ycRazsoE2PZtB/Vjd2n3Wn02yaW+WArI+/6Rr5ZtNu87NrC1saj1uExfOJmuwm2t1tfG1O+8bA0ytjVf39rGUXt7Q5HZTYeZbqVvbhFyy/gy29u2u1Gmrv65de6/Vew3d3KXHHW1id/LGatpu5s1t6Bv0Mkf8r7+pQ3MrFyKp/PDNITyqJvLs7uyua0n/QW3mMzFv0bGy+rWmK9atrbWz9elZ6xvbZqrV18VZqw2q99DdXdL8dI/y3+8yZ+rnT/dXy5cAXj1zpWtBp64vyLsL4z2HfX0BtM/6nLhN3sSx24L7u2X7fvJneTMtrp/XHhV0l8c+q/PSNfL6ZuKX9aGv+y3cJGbSFu/tX1+otzXztaKtPIdqfL3qOuoxZWnZFntM79sGdc0m3s0kA3UzPtaMUEkRvy1a36hS7muN2Ua8/u7h8m7W+9xF0P5CrS4vV9Z2H1kSV3Fzvrf3oGsJ/u4iok1Im75Ne87duqmrvt/VMJHUc3i2KLJpU52FN8Pv2UzP3dSd0duSxsDWVrbjY+uzjT63m1Irbu2N0+1p4TsfDtVtSSXJChb7oSpH/zeP5E1N7K4vC7FhUVN1EH09j6z67PVZkGqKIZbKWEdB/9mVdXHq+6xxT3VbT3dWlN1tTxGpLcF9cLNK9fXa8h1Lm/qM/lV3bc9W3f0mXHif1avVddWLTZ7vNw1dNoXeOC1NXZtzG0nLStKvbmaPq2vfJtj7deO1jjVXhYxij82HYb6nWfPSbNbzb6zQ7muxE9b4fr/Zx/+PNOkVYd8Y2FRkUao/tNSx1nxFm/Jh/1f9Gnc5e9M8tfq/v6kW7KZt0oY/6qoBfk16FevdgDZkmjY73rSFVmV3r7q7zXhNGyieWb1JfRcI6iLhFZz/6ro/qKxidZ1NfH/2Bv1u/n8DoiBZmB4C+eaD1Bp0BTf3hS3m1as+ps/Tqj7X5l16u1F2UP3E5G1gnemqwqr1tfFy/7f8O9j4Q1vvZ1y+KlJ52VLdlYZ92t8mKJ6+TW/32sFmTa3etL9q8TbTwq5Pbc++XftD2aRzXH3q6vvJZv6yBs4eUxY1sdT/qXm/S/rVaRK/NUVazT+q9fHXv7wqJKn99lL3hS5/0U8NY50bvlj5bXLZ1SqWpGvr+j97Ktq6DKKruL+KG+qeS1LJt0RzvHWtWGLLz6i2hZt/+/cCejebVeqC/2abqv7KtSRXrLspKaZW+jWv7fltpvOg+xzrj4X8S9B1vxWxTpCq+SL5d1LlK+rs6eZ3ReI/BGR3c9ydT1DaTKoO1rd3lPaKfIuoDSa3E6rHmouuT1HnpHc6BLs6ysZ9ItyVrD+uqjFb6XLvTkfi9Z3gqxfnS9T+KKn6M9W/zuKdWgCrq6sGpVbYcH35VZ+xTMXq2ADQh7ZP7krK8beir/MqH2Nrg1LXFdS5tBU7yCYKcG6M2PDExu5CdhkE1y/H7B+Ql98ls4O7nH1zA3/l/cnt7dUN1/PxWP/lsW4Dr/f1pLv53Z2bVPYVOreC7+xnRfX/ZRV3tIGuB9ZRQF2/U6cNftNDyk191t0kKnV9F1n1mW7NmVrK9ak8c9x7s7n3uJk5uwU0pU2eG1f/K1YdOHmHXzdBygbr6NfWtq/jPqrP/W2Aqv/YlLt/i9pC/j9tYf2f1bpFxb+hYOW/avm/yapLxZdc4o3GxPVn8Skc56bIh9YQmL6ZqPvLWVUx6bO2HtBmt4vLPOF/VV/XK6ZrIP4nA/J/pV0/1ODUMSa/Bf70ae8L6hQIt5DOpnf8pjbRPql0uE2Q6fcJrjcQjda/L+XqSPWqNDY1mJ4vE9L9Olsl5vcm5ktq1ub/cR1Vrx+nb3Ria7S9s5+TKqD19iwS9tUvzmY04et/T2/2At8W0o7q28+uk3jWZvJoK3rt0qPvWwPeqMGtGfS7Oej1G/btIZ4rz2EjYW+drsEbATfvhqbyVlyU8mTP8mR4dYLHmzVx63cFW1dAm9I1+PlWPhcHpZt3sLfKTdpP1jL2HhO3aWf3m96LTRiBjT83I6uuYD1r08bg3g3PbQuN7VpGy/5/fm5b+BCrDeLdzXeprnJV/Vw2B/g2EY/fnCzX9UjP6ln3snplqLd6STa1c2pWz+qzPAt6Vs96Vs/qAayzeiSzZ/WsntUDWD2rZ/WsHrfsWT2rZ/WsHrfsWT2rZ/WsHsDqWT2rZ/Wsnv3/V1i/Am8B83Ggpc/z4XpWz+rxr3pWz+rxr3pWz+rxsHpWz+pZPesBrJ7Vs3pWz+oBrJ7Vs3pWz/pfW/8fBdnATIsN3cIAAAAASUVORK5CYII="
)
LOGO_BYTES = base64.b64decode(LOGO_BASE64)

# Menu Configuration
MENU = {
    "Breakfast": {
        "Aloo Paratha": 150,
        "Chana": 120,
        "Omelette": 80,
        "Fried Egg": 70,
        "Egg Masala": 130,
        "Tea": 50,
    },
    "Lunch": {
        "Daal Chawal": 200,
        "Anda Tikki": 90,
        "Naan": 40,
        "Raita": 60,
        "Salad": 50,
        "Achaar": 30,
    },
    "Dinner": {
        "Chicken Kabab": 250,
        "Mutton Kabab": 350,
        "Leg Piece": 300,
        "Chest Piece": 280,
        "Tikka Boti": 320,
        "Malai Boti": 330,
    },
}

# Constants
RESTAURANT_NAME = "Affan's Kitchen"
RESTAURANT_TAGLINE = "Tradition in Every Bite"
TAX_RATE = 5  # Default tax rate

# Initialize session state
def init_session_state():
    defaults = {
        "cart": {},
        "order_placed": False,
        "order_history": [],
        "daily_sales": {},
        "inventory": {},
        "current_order_number": 1,
        "tax_rate": TAX_RATE,
        "discount": 0,
        "customer_name": "",
        "customer_phone": "",
        "order_type": "Dine In",
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value
    
    # Initialize inventory if empty
    if not st.session_state.inventory:
        for category, items in MENU.items():
            for item in items:
                st.session_state.inventory[item] = {
                    "stock": 100,
                    "low_stock_threshold": 10,
                    "cost_price": 0,
                }

init_session_state()

# Core Functions
def add_to_cart(item, price, qty=1):
    if qty <= 0:
        return
    # Check inventory
    if st.session_state.inventory[item]["stock"] < qty:
        st.error(f"Insufficient stock for {item}. Available: {st.session_state.inventory[item]['stock']}")
        return False
    
    if item in st.session_state.cart:
        st.session_state.cart[item]["qty"] += qty
    else:
        st.session_state.cart[item] = {"qty": qty, "price": price}
    
    # Update inventory
    st.session_state.inventory[item]["stock"] -= qty
    st.session_state.order_placed = False
    return True

def remove_from_cart(item):
    if item in st.session_state.cart:
        # Return to inventory
        qty = st.session_state.cart[item]["qty"]
        st.session_state.inventory[item]["stock"] += qty
        del st.session_state.cart[item]
    st.session_state.order_placed = False

def clear_cart():
    # Return all items to inventory
    for item, data in st.session_state.cart.items():
        st.session_state.inventory[item]["stock"] += data["qty"]
    st.session_state.cart = {}
    st.session_state.order_placed = False
    # Clear quantity inputs
    for key in list(st.session_state.keys()):
        if key.startswith("qty_"):
            del st.session_state[key]

def generate_receipt():
    order_time = datetime.now().strftime("%d-%m-%Y %I:%M %p")
    order_number = f"ORD-{datetime.now().strftime('%y%m%d')}-{st.session_state.current_order_number:04d}"
    
    total = sum(d["qty"] * d["price"] for d in st.session_state.cart.values())
    tax_rate = st.session_state.tax_rate
    tax_amount = round(total * tax_rate / 100)
    discount = st.session_state.discount
    grand_total = total + tax_amount - discount
    
    receipt_lines = []
    receipt_lines.append(RESTAURANT_NAME.center(40))
    receipt_lines.append(RESTAURANT_TAGLINE.center(40))
    receipt_lines.append("=" * 40)
    receipt_lines.append(f"Order #: {order_number}")
    receipt_lines.append(f"Date: {order_time}")
    receipt_lines.append(f"Customer: {st.session_state.customer_name or 'Walk-in'}")
    receipt_lines.append(f"Type: {st.session_state.order_type}")
    receipt_lines.append("=" * 40)
    receipt_lines.append(f"{'Item':<20}{'Qty':>6}{'Price':>10}{'Total':>10}")
    receipt_lines.append("-" * 40)
    
    for item, data in st.session_state.cart.items():
        qty = data["qty"]
        price = data["price"]
        line_total = qty * price
        receipt_lines.append(f"{item[:20]:<20}{qty:>6}{price:>10}{line_total:>10}")
    
    receipt_lines.append("=" * 40)
    receipt_lines.append(f"{'Subtotal':<36}{total:>10}")
    receipt_lines.append(f"{'Tax/Service (' + str(tax_rate) + '%)':<36}{tax_amount:>10}")
    if discount > 0:
        receipt_lines.append(f"{'Discount':<36}{'-' + str(discount):>10}")
    receipt_lines.append(f"{'TOTAL':<36}{grand_total:>10}")
    receipt_lines.append("=" * 40)
    receipt_lines.append("Thank you for dining with us!".center(40))
    receipt_lines.append("Please visit again!".center(40))
    
    return "\n".join(receipt_lines), order_number, order_time, grand_total

def save_order_to_history(receipt_text, order_number, order_time, grand_total):
    order_data = {
        "order_number": order_number,
        "date": order_time,
        "customer": st.session_state.customer_name or "Walk-in",
        "order_type": st.session_state.order_type,
        "items": st.session_state.cart.copy(),
        "total": grand_total,
        "receipt": receipt_text,
        "timestamp": datetime.now().isoformat()
    }
    st.session_state.order_history.append(order_data)
    st.session_state.current_order_number += 1
    
    # Update daily sales
    today = date.today().isoformat()
    if today not in st.session_state.daily_sales:
        st.session_state.daily_sales[today] = {
            "orders": [],
            "total_sales": 0,
            "total_items": 0,
            "categories": {}
        }
    
    daily = st.session_state.daily_sales[today]
    daily["orders"].append(order_number)
    daily["total_sales"] += grand_total
    daily["total_items"] += sum(d["qty"] for d in st.session_state.cart.values())
    
    # Update category sales
    for item, data in st.session_state.cart.items():
        category = next((cat for cat, items in MENU.items() if item in items), "Other")
        if category not in daily["categories"]:
            daily["categories"][category] = {"count": 0, "revenue": 0}
        daily["categories"][category]["count"] += data["qty"]
        daily["categories"][category]["revenue"] += data["qty"] * data["price"]

# UI Layout
# Header
col1, col2, col3 = st.columns([1, 3, 1])
with col1:
    st.image(LOGO_BYTES, width=110)
with col2:
    st.title(RESTAURANT_NAME)
    st.caption(RESTAURANT_TAGLINE)
with col3:
    # Quick stats
    today = date.today().isoformat()
    if today in st.session_state.daily_sales:
        daily_total = st.session_state.daily_sales[today]["total_sales"]
        daily_items = st.session_state.daily_sales[today]["total_items"]
        st.metric("Today's Sales", f"Rs. {daily_total:,}", f"{daily_items} items")

st.divider()

# Main Layout
menu_col, cart_col, analytics_col = st.tabs(["📋 Menu & Order", "🧾 Cart & Checkout", "📊 Analytics"])

with menu_col:
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("📋 Menu")
        
        # Customer Info
        with st.expander("👤 Customer Details", expanded=False):
            col_a, col_b, col_c = st.columns(3)
            with col_a:
                st.session_state.customer_name = st.text_input("Customer Name", value=st.session_state.customer_name)
            with col_b:
                st.session_state.customer_phone = st.text_input("Phone", value=st.session_state.customer_phone)
            with col_c:
                st.session_state.order_type = st.selectbox("Order Type", ["Dine In", "Takeaway", "Delivery"])
        
        # Menu Tabs
        tabs = st.tabs(list(MENU.keys()))
        for tab, category in zip(tabs, MENU.keys()):
            with tab:
                # Category header with order count
                total_category_items = sum(1 for item in MENU[category] 
                                         if st.session_state.get(f"qty_{category}_{item}", 0) > 0)
                if total_category_items > 0:
                    st.info(f"🛒 {total_category_items} items in cart from this category")
                
                for item, price in MENU[category].items():
                    col_item, col_price, col_qty = st.columns([3, 1, 2])
                    
                    with col_item:
                        # Show stock status
                        stock = st.session_state.inventory[item]["stock"]
                        stock_emoji = "🟢" if stock > 10 else "🟡" if stock > 5 else "🔴"
                        st.write(f"**{item}** {stock_emoji}")
                    
                    with col_price:
                        st.write(f"Rs. {price}")
                    
                    with col_qty:
                        qty_key = f"qty_{category}_{item}"
                        if qty_key not in st.session_state:
                            st.session_state[qty_key] = 0
                        
                        col_minus, col_num, col_plus = st.columns([1, 2, 1])
                        
                        if col_minus.button("−", key=f"minus_{qty_key}", disabled=st.session_state[qty_key] == 0):
                            st.session_state[qty_key] -= 1
                            if st.session_state[qty_key] == 0:
                                remove_from_cart(item)
                            else:
                                if item in st.session_state.cart:
                                    st.session_state.cart[item]["qty"] = st.session_state[qty_key]
                            st.rerun()
                        
                        col_num.number_input("", key=qty_key, min_value=0, max_value=min(50, st.session_state.inventory[item]["stock"]), 
                                           step=1, label_visibility="collapsed")
                        
                        if col_plus.button("+", key=f"plus_{qty_key}", disabled=st.session_state[qty_key] >= st.session_state.inventory[item]["stock"]):
                            st.session_state[qty_key] += 1
                            if add_to_cart(item, price, 1):
                                st.rerun()
                            else:
                                st.session_state[qty_key] -= 1

with cart_col:
    st.subheader("🧾 Current Order")
    
    if not st.session_state.cart:
        st.info("No items in cart. Add items from the menu.")
    else:
        # Cart Items
        total = 0
        total_items = 0
        for item, data in list(st.session_state.cart.items()):
            qty = data["qty"]
            price = data["price"]
            line_total = qty * price
            total += line_total
            total_items += qty
            
            col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
            col1.write(f"{item}")
            col2.write(f"x{qty}")
            col3.write(f"Rs. {line_total}")
            if col4.button("❌", key=f"remove_{item}"):
                remove_from_cart(item)
                st.rerun()
        
        st.divider()
        
        # Order Summary
        col1, col2 = st.columns(2)
        with col1:
            st.session_state.tax_rate = st.number_input("Tax %", min_value=0, max_value=30, 
                                                       value=st.session_state.tax_rate, step=1)
        with col2:
            st.session_state.discount = st.number_input("Discount Rs.", min_value=0, 
                                                       value=st.session_state.discount, step=10)
        
        tax_amount = round(total * st.session_state.tax_rate / 100)
        grand_total = total + tax_amount - st.session_state.discount
        
        st.write(f"Items: **{total_items}**")
        st.write(f"Subtotal: **Rs. {total:,}**")
        st.write(f"Tax ({st.session_state.tax_rate}%): **Rs. {tax_amount:,}**")
        if st.session_state.discount > 0:
            st.write(f"Discount: **-Rs. {st.session_state.discount:,}**")
        st.markdown(f"### Grand Total: Rs. {grand_total:,}")
        
        # Action Buttons
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("✅ Place Order", use_container_width=True):
                if st.session_state.cart:
                    st.session_state.order_placed = True
                    receipt_text, order_number, order_time, grand_total = generate_receipt()
                    save_order_to_history(receipt_text, order_number, order_time, grand_total)
                    st.success(f"Order {order_number} placed successfully!")
                    st.balloons()
                else:
                    st.warning("Cart is empty!")
        
        with col2:
            if st.button("🗑️ Clear Cart", use_container_width=True):
                clear_cart()
                st.rerun()
        
        with col3:
            if st.button("📝 Quick Order", use_container_width=True):
                # Pre-set a sample order for quick testing
                sample_items = list(st.session_state.cart.keys())
                if not sample_items:
                    # Add sample items
                    for category, items in MENU.items():
                        for item, price in list(items.items())[:2]:
                            add_to_cart(item, price, 1)
                    st.rerun()
    
    # Order History Preview
    with st.expander("📜 Recent Orders", expanded=False):
        if st.session_state.order_history:
            recent = st.session_state.order_history[-5:]
            for order in reversed(recent):
                st.caption(f"**{order['order_number']}** - {order['date']} - Rs. {order['total']:,}")
        else:
            st.info("No orders yet")

with analytics_col:
    st.subheader("📊 Daily Analytics")
    
    # Date selector
    col1, col2 = st.columns(2)
    with col1:
        view_date = st.date_input("Select Date", date.today())
    with col2:
        if st.button("Refresh Data"):
            st.rerun()
    
    date_str = view_date.isoformat()
    
    if date_str in st.session_state.daily_sales:
        daily = st.session_state.daily_sales[date_str]
        
        # Key Metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Sales", f"Rs. {daily['total_sales']:,}")
        with col2:
            st.metric("Total Items", daily['total_items'])
        with col3:
            st.metric("Orders", len(daily['orders']))
        with col4:
            avg_order = daily['total_sales'] / len(daily['orders']) if daily['orders'] else 0
            st.metric("Avg. Order", f"Rs. {avg_order:,.0f}")
        
        st.divider()
        
        # Category Breakdown
        if daily['categories']:
            st.subheader("Category Performance")
            cat_data = []
            for cat, data in daily['categories'].items():
                cat_data.append({
                    "Category": cat,
                    "Items Sold": data['count'],
                    "Revenue": data['revenue']
                })
            
            df = pd.DataFrame(cat_data)
            
            col1, col2 = st.columns(2)
            with col1:
                fig = px.bar(df, x='Category', y='Items Sold', title='Items by Category')
                st.plotly_chart(fig, use_container_width=True)
            with col2:
                fig = px.pie(df, values='Revenue', names='Category', title='Revenue by Category')
                st.plotly_chart(fig, use_container_width=True)
        
        # Recent Orders
        with st.expander("📋 Daily Orders Detail", expanded=False):
            for order_num in daily['orders']:
                # Find order in history
                for order in st.session_state.order_history:
                    if order['order_number'] == order_num:
                        st.caption(f"**{order['order_number']}** | {order['date']} | Rs. {order['total']:,}")
                        break
    else:
        st.info(f"No sales data available for {view_date.strftime('%B %d, %Y')}")
    
    # Overall Statistics
    with st.expander("📈 Overall Statistics", expanded=False):
        if st.session_state.order_history:
            total_sales = sum(order['total'] for order in st.session_state.order_history)
            total_orders = len(st.session_state.order_history)
            total_items = sum(sum(item['qty'] for item in order['items'].values()) for order in st.session_state.order_history)
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Orders", total_orders)
            with col2:
                st.metric("Total Revenue", f"Rs. {total_sales:,}")
            with col3:
                st.metric("Total Items Sold", total_items)
            
            # Export options
            if st.button("📥 Export Data (CSV)"):
                data = []
                for order in st.session_state.order_history:
                    data.append({
                        "Order #": order['order_number'],
                        "Date": order['date'],
                        "Customer": order['customer'],
                        "Type": order['order_type'],
                        "Total": order['total'],
                    })
                df = pd.DataFrame(data)
                csv = df.to_csv(index=False)
                st.download_button(
                    "Download CSV",
                    data=csv,
                    file_name=f"sales_data_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv",
                )

# Receipt Display
if st.session_state.order_placed and st.session_state.cart:
    st.divider()
    st.subheader("🖨️ Receipt")
    
    receipt_text, order_number, order_time, grand_total = generate_receipt()
    
    # Display receipt
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.image(LOGO_BYTES, width=100)
        st.code(receipt_text, language=None)
        
        # Action buttons
        col_a, col_b, col_c = st.columns(3)
        with col_a:
            st.download_button(
                "⬇️ Download",
                data=receipt_text,
                file_name=f"receipt_{order_number}.txt",
                mime="text/plain",
                use_container_width=True
            )
        with col_b:
            # Print function
            logo_data_uri = "data:image/png;base64," + LOGO_BASE64
            print_html = f'''
            <div id="receipt-print" style="display:none;">
                <div style="text-align:center;">
                    <img src="{logo_data_uri}" style="width:80px;"/>
                </div>
                <pre style="font-family: monospace; white-space: pre;">{receipt_text}</pre>
            </div>
            <button onclick="printReceipt()" style="padding:10px 20px; font-size:16px; cursor:pointer; background:#4CAF50; color:white; border:none; border-radius:5px;">
                🖨️ Print
            </button>
            <script>
            function printReceipt() {{
                var content = document.getElementById('receipt-print').innerHTML;
                var printWindow = window.open('', '', 'width=400,height=650');
                printWindow.document.write('<div style="font-size:14px;">' + content + '</div>');
                printWindow.document.close();
                printWindow.print();
            }}
            </script>
            '''
            st.components.v1.html(print_html, height=70)
        with col_c:
            if st.button("✅ New Order", use_container_width=True):
                clear_cart()
                st.session_state.order_placed = False
                st.rerun()

# Auto-clear order placed state after showing receipt
if st.session_state.order_placed and not st.session_state.cart:
    st.session_state.order_placed = False

# Footer
st.divider()
st.caption(f"© 2024 {RESTAURANT_NAME} - Professional POS System")
st.caption(f"Version 2.0 | Orders Today: {len(st.session_state.daily_sales.get(date.today().isoformat(), {}).get('orders', []))}")
