import { Composition, Still } from "remotion";
import { LongForm } from "./LongForm";
import { Thumb } from "./Thumb";
import { DURATION, FPS, H, W } from "./theme";

export const Root = () => (
  <>
    <Composition id="LongForm" component={LongForm} durationInFrames={DURATION} fps={FPS} width={W} height={H} />
    <Still id="Thumb" component={Thumb} width={W} height={H} />
  </>
);
