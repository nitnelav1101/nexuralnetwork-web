# neXuralNetwork WEB #

## Running on Windows ##
Firstly you need to install the following softwares/dependencies:
 * Python - you need to have a Python distribution installed in your machine (preferable [Anaconda](https://www.continuum.io/downloads));
 * [Redis](https://redis.io) 
 * [nexuralNetwork](https://github.com/nitnelav1101/nexuralnetwork)
 
 Type the following to run the neXuralNetworkWEB:
 ```
git clone https://github.com/nitnelav1101/nexuralnetwork-web.git
cd nexuralnetwork-web
pip install -r requirements.txt
cd nexuralnetweb
runFlaskServer.bat
runCeleryServer.bat
 ```
By default, Flask will run the website on http://localhost:5000

## License ##
neXuralNetworkWEB is licensed under the MIT License. See the [LICENSE](LICENSE.md) for the specific language governing permissions and limitations under the License.
