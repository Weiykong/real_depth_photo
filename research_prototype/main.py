import os
import cv2
import numpy as np
from depth_engine import DepthEngine
from lens_sim import apply_variable_blur, apply_tilt_shift, apply_vignette
from evaluator import pick_hero_frame, get_sharpness_score
from refiner import DepthRefiner

# Global focus state
current_focus_depth = 255
needs_update = True


def mouse_callback(event, x, y, flags, param):
    """Handles the user clicking on the image to select a focus point."""
    global current_focus_depth, needs_update
    if event == cv2.EVENT_LBUTTONDOWN:
        depth_map = param['depth_map']
        scale_x = int(x * (param['width'] / param['view_w']))
        scale_y = int(y * (param['height'] / param['view_h']))
        scale_x = min(scale_x, param['width'] - 1)
        scale_y = min(scale_y, param['height'] - 1)
        current_focus_depth = depth_map[scale_y, scale_x]
        needs_update = True
        print(f"Focus set to depth: {current_focus_depth} (Coordinate: {scale_x}, {scale_y})")


def run_lsdr_app(burst_folder):
    """Full interactive mode — processes 4K frames with real-time focus selection."""
    global current_focus_depth, needs_update

    print("Loading 4K burst images...")
    files = sorted([
        os.path.join(burst_folder, f)
        for f in os.listdir(burst_folder)
        if f.lower().endswith(('.jpg', '.jpeg', '.png', '.tiff', '.bmp'))
    ])
    images = [cv2.imread(f) for f in files]
    images = [img for img in images if img is not None]

    if not images:
        print("No valid images found in the specified folder.")
        return

    hero_idx = pick_hero_frame(images)
    hero_frame = images[hero_idx]
    h, w = hero_frame.shape[:2]
    print(f"Hero frame selected: {files[hero_idx]} ({w}x{h})")

    engine = DepthEngine()
    depth_map = engine.generate_map(hero_frame)

    preview_w = min(1280, w)
    preview_h = int(h * (preview_w / w))
    hero_preview = cv2.resize(hero_frame, (preview_w, preview_h))
    depth_preview = cv2.resize(depth_map, (preview_w, preview_h))

    window_name = "Real Depth Photo — Click to Focus"
    cv2.namedWindow(window_name, cv2.WINDOW_AUTOSIZE)
    cv2.setMouseCallback(window_name, mouse_callback, {
        'depth_map': depth_map,
        'width': w, 'height': h,
        'view_w': preview_w, 'view_h': preview_h
    })

    print("\n--- CONTROLS ---")
    print("  LEFT CLICK : Set focus at that depth")
    print("  S          : Save 4K high-quality result")
    print("  R          : Refine depth map (multi-view)")
    print("  D          : Toggle depth map view")
    print("  T          : Toggle tilt-shift mode")
    print("  V          : Toggle vignette")
    print("  Q          : Quit")

    show_depth = False
    tilt_shift_mode = False
    vignette_on = False
    display_img = hero_preview.copy()

    while True:
        if needs_update:
            if tilt_shift_mode:
                display_img = apply_tilt_shift(
                    hero_preview,
                    band_center=0.5,
                    band_width=0.15,
                    max_blur=15,
                    vignette_strength=0.25
                )
            else:
                display_img = apply_variable_blur(
                    hero_preview, depth_preview,
                    focus_depth=current_focus_depth,
                    max_bokeh=15,
                    premium_look=True,
                    cats_eye_strength=0.22,
                    flare_strength=0.06,
                    vignette_strength=0.20 if vignette_on else 0.0
                )
            needs_update = False

        if show_depth:
            depth_colored = cv2.applyColorMap(depth_preview, cv2.COLORMAP_INFERNO)
            cv2.imshow(window_name, depth_colored)
        else:
            cv2.imshow(window_name, display_img)

        key = cv2.waitKey(30) & 0xFF

        if key == ord('r'):
            if len(files) < 2:
                print("Need at least 2 images for multi-view refinement.")
                continue
            print("Running Multi-View Refinement...")
            refiner = DepthRefiner()
            second_frame = cv2.imread(files[1 if hero_idx != 1 else 0])
            depth_map = refiner.refine(hero_frame, second_frame, depth_map)
            depth_preview = cv2.resize(depth_map, (preview_w, preview_h))
            needs_update = True
            print("Refinement complete — edges should be sharper.")

        elif key == ord('d'):
            show_depth = not show_depth

        elif key == ord('t'):
            tilt_shift_mode = not tilt_shift_mode
            needs_update = True
            print(f"Tilt-shift mode: {'ON' if tilt_shift_mode else 'OFF'}")

        elif key == ord('v'):
            vignette_on = not vignette_on
            needs_update = True
            print(f"Vignette: {'ON' if vignette_on else 'OFF'}")

        elif key == ord('s'):
            print("Processing 4K final render...")
            if tilt_shift_mode:
                final_4k = apply_tilt_shift(
                    hero_frame,
                    band_center=0.5,
                    band_width=0.15,
                    max_blur=25,
                    vignette_strength=0.25
                )
                save_path = "final_4k_tiltshift.jpg"
            else:
                final_4k = apply_variable_blur(
                    hero_frame, depth_map,
                    focus_depth=current_focus_depth,
                    max_bokeh=20,
                    premium_look=True,
                    cats_eye_strength=0.32,
                    flare_strength=0.10,
                    vignette_strength=0.20 if vignette_on else 0.0
                )
                save_path = f"final_4k_focus_{current_focus_depth}.jpg"
            cv2.imwrite(save_path, final_4k, [int(cv2.IMWRITE_JPEG_QUALITY), 98])
            print(f"Saved: {save_path}")

        elif key == ord('q'):
            break

    cv2.destroyAllWindows()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Real Depth Photo — AI-powered depth-of-field")
    parser.add_argument("burst_folder",
                        help="Path to folder containing burst images")
    args = parser.parse_args()
    run_lsdr_app(args.burst_folder)
