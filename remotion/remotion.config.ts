import { Config } from "@remotion/cli/config";
// macOS: use the installed Chrome (headless-shell spawn error -88, README §19)
Config.setBrowserExecutable("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome");
Config.setVideoImageFormat("jpeg");
Config.setCodec("h264");
Config.setCrf(18);
