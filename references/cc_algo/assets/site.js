(() => {
  const images = [...document.querySelectorAll('img.algo-figure')];
  if (!images.length) return;

  const viewer = document.createElement('dialog');
  viewer.className = 'image-viewer';
  viewer.setAttribute('aria-labelledby', 'image-viewer-title');
  viewer.innerHTML = `
    <div class="image-viewer-shell">
      <header class="image-viewer-toolbar">
        <strong id="image-viewer-title">查看图像</strong>
        <div class="image-viewer-actions" aria-label="图像缩放控制">
          <button type="button" data-viewer-action="out" aria-label="缩小">−</button>
          <output data-viewer-scale aria-live="polite">100%</output>
          <button type="button" data-viewer-action="in" aria-label="放大">＋</button>
          <button type="button" data-viewer-action="reset">适应窗口</button>
          <button type="button" data-viewer-action="close" class="viewer-close" aria-label="关闭图像">关闭</button>
        </div>
      </header>
      <div class="image-viewer-stage" tabindex="0" role="region" aria-label="可缩放图像查看区" aria-describedby="image-viewer-help">
        <img class="image-viewer-image" alt="">
      </div>
      <p class="image-viewer-help" id="image-viewer-help">滚轮或＋／－缩放 · 放大后按住鼠标左键拖动 · 0恢复窗口 · Esc关闭</p>
    </div>`;
  document.body.append(viewer);

  const stage = viewer.querySelector('.image-viewer-stage');
  const fullImage = viewer.querySelector('.image-viewer-image');
  const title = viewer.querySelector('#image-viewer-title');
  const scaleOutput = viewer.querySelector('[data-viewer-scale]');
  const ZOOM_STEPS = [50, 75, 100, 125, 150, 175, 200, 225, 250, 275, 300, 325, 350, 375, 400];
  let scale = 1;
  let dragging = false;
  let dragPointerId = null;
  let dragStartX = 0;
  let dragStartY = 0;
  let dragStartLeft = 0;
  let dragStartTop = 0;
  fullImage.draggable = false;

  const setScale = (next) => {
    scale = Math.min(4, Math.max(0.5, Math.round(next * 100) / 100));
    for (const percent of ZOOM_STEPS) fullImage.classList.remove(`zoom-${percent}`);
    fullImage.classList.add(`zoom-${Math.round(scale * 100)}`);
    scaleOutput.value = `${Math.round(scale * 100)}%`;
    scaleOutput.textContent = scaleOutput.value;
    stage.classList.toggle('is-pannable', scale > 1);
    if (scale <= 1) {
      dragging = false;
      dragPointerId = null;
      stage.classList.remove('is-dragging');
      stage.scrollTo({left: 0, top: 0});
    }
  };

  const stopDragging = (event) => {
    if (!dragging || event.pointerId !== dragPointerId) return;
    dragging = false;
    dragPointerId = null;
    stage.classList.remove('is-dragging');
    if (stage.hasPointerCapture(event.pointerId)) stage.releasePointerCapture(event.pointerId);
  };

  const closeViewer = () => {
    if (viewer.open) viewer.close();
  };

  const openViewer = (source) => {
    fullImage.src = source.currentSrc || source.src;
    fullImage.alt = source.alt || '算法图像';
    title.textContent = source.alt || '查看图像';
    setScale(1);
    stage.scrollTo({left: 0, top: 0});
    viewer.showModal();
    document.body.classList.add('viewer-open');
    stage.focus();
  };

  viewer.addEventListener('close', () => {
    document.body.classList.remove('viewer-open');
    fullImage.removeAttribute('src');
  });
  viewer.addEventListener('click', (event) => {
    if (event.target === viewer) closeViewer();
  });
  viewer.querySelector('[data-viewer-action="in"]').addEventListener('click', () => setScale(scale + 0.25));
  viewer.querySelector('[data-viewer-action="out"]').addEventListener('click', () => setScale(scale - 0.25));
  viewer.querySelector('[data-viewer-action="reset"]').addEventListener('click', () => setScale(1));
  viewer.querySelector('[data-viewer-action="close"]').addEventListener('click', closeViewer);
  stage.addEventListener('wheel', (event) => {
    event.preventDefault();
    setScale(scale + (event.deltaY < 0 ? 0.25 : -0.25));
  }, {passive: false});
  stage.addEventListener('pointerdown', (event) => {
    if (event.button !== 0 || scale <= 1) return;
    dragging = true;
    dragPointerId = event.pointerId;
    dragStartX = event.clientX;
    dragStartY = event.clientY;
    dragStartLeft = stage.scrollLeft;
    dragStartTop = stage.scrollTop;
    stage.classList.add('is-dragging');
    stage.setPointerCapture(event.pointerId);
    event.preventDefault();
  });
  stage.addEventListener('pointermove', (event) => {
    if (!dragging || event.pointerId !== dragPointerId) return;
    stage.scrollLeft = dragStartLeft - (event.clientX - dragStartX);
    stage.scrollTop = dragStartTop - (event.clientY - dragStartY);
  });
  stage.addEventListener('pointerup', stopDragging);
  stage.addEventListener('pointercancel', stopDragging);
  stage.addEventListener('dragstart', (event) => event.preventDefault());
  viewer.addEventListener('keydown', (event) => {
    if (event.key === '+' || event.key === '=') setScale(scale + 0.25);
    if (event.key === '-') setScale(scale - 0.25);
    if (event.key === '0') setScale(1);
  });

  images.forEach((image) => {
    const button = image.closest('.figure-zoom-trigger');
    const trigger = button || image;
    image.dataset.zoomable = 'true';
    image.title = '点击放大查看';
    if (!button) {
      image.tabIndex = 0;
      image.setAttribute('role', 'button');
      image.setAttribute('aria-label', `放大查看：${image.alt || '算法图像'}`);
    }
    trigger.addEventListener('click', (event) => {
      event.preventDefault();
      openViewer(image);
    });
    if (!button) {
      trigger.addEventListener('keydown', (event) => {
        if (event.key === 'Enter' || event.key === ' ') {
          event.preventDefault();
          openViewer(image);
        }
      });
    }
  });
})();
