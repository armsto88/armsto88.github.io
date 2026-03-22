class STLViewer extends HTMLElement {
  constructor() {
    super();
    this.connected = false;
    this.resizeHandler = null;
  }

  connectedCallback() {
    this.connected = true;

    if (!this.hasAttribute('model')) {
      this.innerHTML = '<p style="color:red;font-size:12px;">No STL file specified</p>';
      return;
    }

    const waitForDeps = () => {
      if (!window.THREE || !window.THREE.OrbitControls || !window.THREE.STLLoader) {
        setTimeout(waitForDeps, 60);
        return;
      }
      this.initViewer();
    };

    waitForDeps();
  }

  initViewer() {
    try {
      const root = this.shadowRoot || this.attachShadow({ mode: 'open' });
      root.innerHTML = '';

      const modelPath = this.getAttribute('model');
      const modelUrl = new URL(modelPath, document.baseURI).href;
      const colorAttr = this.getAttribute('color') || '#2d6a4f';
      const bgAttr = this.getAttribute('background') || '#1f2428';
      const rotateSpeedAttr = parseFloat(this.getAttribute('rotate-speed') || '0.25');
      const cameraDistanceAttr = parseFloat(this.getAttribute('camera-distance') || '130');

      const container = document.createElement('div');
      container.style.cssText = `width:100%;height:100%;background:${bgAttr};`;
      root.appendChild(container);

      const width = Math.max(container.clientWidth || this.clientWidth || 300, 200);
      const height = Math.max(container.clientHeight || this.clientHeight || 280, 200);

      const scene = new THREE.Scene();
      scene.background = new THREE.Color(bgAttr);

      const camera = new THREE.PerspectiveCamera(65, width / height, 0.1, 5000);
      camera.position.set(0, 0, 120);

      const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
      renderer.setPixelRatio(window.devicePixelRatio || 1);
      renderer.setSize(width, height);
      renderer.outputEncoding = THREE.sRGBEncoding;
      renderer.toneMapping = THREE.ACESFilmicToneMapping;
      renderer.toneMappingExposure = 0.95;
      container.appendChild(renderer.domElement);

      scene.add(new THREE.HemisphereLight(0xe9edf2, 0x3a3f47, 0.75));
      const dir = new THREE.DirectionalLight(0xf7f3ea, 0.38);
      dir.position.set(1.2, 1, 1.5);
      scene.add(dir);

      const controls = new THREE.OrbitControls(camera, renderer.domElement);
      controls.enableDamping = true;
      controls.autoRotate = true;
      controls.autoRotateSpeed = Number.isFinite(rotateSpeedAttr) ? rotateSpeedAttr : 0.25;

      const loader = new THREE.STLLoader();
      loader.load(
        modelUrl,
        (geometry) => {
          geometry.computeBoundingBox();
          const center = new THREE.Vector3();
          geometry.boundingBox.getCenter(center);
          geometry.translate(-center.x, -center.y, -center.z);

          const size = geometry.boundingBox.getSize(new THREE.Vector3());
          const maxDim = Math.max(size.x, size.y, size.z) || 1;
          const scale = 80 / maxDim;
          geometry.scale(scale, scale, scale);

          let meshColor = 0x2d6a4f;
          try {
            meshColor = new THREE.Color(colorAttr).getHex();
          } catch (e) {
            meshColor = 0x2d6a4f;
          }

          const mesh = new THREE.Mesh(
            geometry,
            new THREE.MeshStandardMaterial({
              color: meshColor,
              roughness: 0.74,
              metalness: 0.04
            })
          );
          mesh.rotation.x = -Math.PI / 2;
          mesh.rotation.z = 0.32;
          scene.add(mesh);

          // Start with a side-on profile view instead of top-down.
          const cameraDistance = Number.isFinite(cameraDistanceAttr) ? cameraDistanceAttr : 130;
          camera.position.set(cameraDistance, cameraDistance * 0.123, 0);
          controls.target.set(0, 0, 0);
          controls.update();

          const animate = () => {
            if (!this.connected) return;
            requestAnimationFrame(animate);
            controls.update();
            renderer.render(scene, camera);
          };
          animate();
        },
        undefined,
        (err) => {
          console.error('stl-viewer: failed loading', modelUrl, err);
          container.innerHTML = '<p style="color:red;font-size:12px;padding:12px;text-align:center;">Failed to load STL model</p>';
        }
      );

      this.resizeHandler = () => {
        const w = Math.max(container.clientWidth || this.clientWidth || 300, 200);
        const h = Math.max(container.clientHeight || this.clientHeight || 280, 200);
        camera.aspect = w / h;
        camera.updateProjectionMatrix();
        renderer.setSize(w, h);
      };
      window.addEventListener('resize', this.resizeHandler);
    } catch (err) {
      console.error('stl-viewer: init error', err);
      this.innerHTML = '<p style="color:red;font-size:12px;">Error initializing viewer</p>';
    }
  }

  disconnectedCallback() {
    this.connected = false;
    if (this.resizeHandler) {
      window.removeEventListener('resize', this.resizeHandler);
      this.resizeHandler = null;
    }
  }
}

customElements.define('stl-viewer', STLViewer);
