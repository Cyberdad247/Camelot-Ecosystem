"use client";

import { useEffect, useRef } from "react";
import { Box3, Clock, DirectionalLight, HemisphereLight, PerspectiveCamera, Scene, Vector3, WebGLRenderer } from "three";
import { GLTFLoader } from "three/addons/loaders/GLTFLoader.js";
import { VRMLoaderPlugin, VRMUtils, type VRM } from "@pixiv/three-vrm";
import type { AnyaPerceptionSignal } from "@/hooks/use-anya-perception";

export default function AnyaVrmStage({ modelUrl, speaking, signal, reduced, onReady, onError }: {
  modelUrl: string;
  speaking: boolean;
  signal: AnyaPerceptionSignal;
  reduced: boolean;
  onReady: () => void;
  onError: () => void;
}) {
  const mountRef = useRef<HTMLDivElement | null>(null);
  const signalRef = useRef(signal);
  const speakingRef = useRef(speaking);
  signalRef.current = signal;
  speakingRef.current = speaking;

  useEffect(() => {
    const mount = mountRef.current;
    if (!mount) return;

    let disposed = false;
    let frame = 0;
    let currentVrm: VRM | null = null;
    let lastRender = 0;
    const renderer = new WebGLRenderer({ alpha: true, antialias: !reduced, powerPreference: reduced ? "low-power" : "high-performance" });
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, reduced ? 1 : 1.5));
    renderer.setClearAlpha(0);
    mount.appendChild(renderer.domElement);
    const scene = new Scene();
    const camera = new PerspectiveCamera(25, 1, 0.1, 100);
    camera.position.set(0, 1.25, 4.3);
    scene.add(new HemisphereLight(0xf4dca1, 0x173834, 2.2));
    const key = new DirectionalLight(0xffffff, 2.4);
    key.position.set(1.5, 2.5, 3);
    scene.add(key);

    const resize = () => {
      const width = Math.max(1, mount.clientWidth);
      const height = Math.max(1, mount.clientHeight);
      renderer.setSize(width, height, false);
      camera.aspect = width / height;
      camera.updateProjectionMatrix();
    };
    const observer = new ResizeObserver(resize);
    observer.observe(mount);
    resize();

    const loader = new GLTFLoader();
    loader.register((parser) => new VRMLoaderPlugin(parser));
    loader.load(modelUrl, (gltf) => {
      if (disposed) return;
      const vrm = gltf.userData.vrm as VRM | undefined;
      if (!vrm) {
        onError();
        return;
      }
      VRMUtils.removeUnnecessaryVertices(gltf.scene);
      VRMUtils.combineSkeletons(gltf.scene);
      vrm.scene.traverse((object) => { object.frustumCulled = false; });
      const bounds = new Box3().setFromObject(vrm.scene);
      const size = bounds.getSize(new Vector3());
      const center = bounds.getCenter(new Vector3());
      vrm.scene.position.sub(center);
      vrm.scene.position.y += size.y * 0.5 - 1.05;
      const scale = 2.15 / Math.max(size.y, 0.1);
      vrm.scene.scale.setScalar(scale);
      scene.add(vrm.scene);
      currentVrm = vrm;
      onReady();
    }, undefined, onError);

    const clock = new Clock();
    const animate = (timestamp: number) => {
      if (disposed) return;
      frame = requestAnimationFrame(animate);
      const minimumFrameTime = reduced ? 1000 / 30 : 1000 / 60;
      if (timestamp - lastRender < minimumFrameTime) return;
      lastRender = timestamp;
      const delta = Math.min(clock.getDelta(), 0.05);
      if (currentVrm) {
        const currentSignal = signalRef.current;
        const manager = currentVrm.expressionManager;
        manager?.setValue("blink", currentSignal.blink);
        manager?.setValue("aa", speakingRef.current ? 0.25 + currentSignal.mouthOpen * 0.75 : currentSignal.mouthOpen * 0.35);
        manager?.setValue("lookLeft", Math.max(0, -currentSignal.gazeX));
        manager?.setValue("lookRight", Math.max(0, currentSignal.gazeX));
        manager?.setValue("lookUp", Math.max(0, -currentSignal.gazeY));
        manager?.setValue("lookDown", Math.max(0, currentSignal.gazeY));
        currentVrm.scene.rotation.y = Math.sin(clock.elapsedTime * 0.45) * 0.018;
        currentVrm.update(delta);
      }
      renderer.render(scene, camera);
    };
    frame = requestAnimationFrame(animate);

    return () => {
      disposed = true;
      cancelAnimationFrame(frame);
      observer.disconnect();
      if (currentVrm) {
        scene.remove(currentVrm.scene);
        VRMUtils.deepDispose(currentVrm.scene);
      }
      renderer.dispose();
      renderer.domElement.remove();
    };
  }, [modelUrl, onError, onReady, reduced]);

  return <div ref={mountRef} className="anya-vrm-stage" aria-hidden="true" />;
}
