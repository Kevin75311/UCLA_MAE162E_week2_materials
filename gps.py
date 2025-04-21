import socket
import numpy as np
import math
import matplotlib.pyplot as plt

# === Configuration ===
PORT = 5487
NUM_NODES = 4
Z_TAG = 1.0  # Tag height in meters
M_TO_FEET = 3.28084  # Conversion factor

# === Anchor positions in BLOCK UNITS (converted to feet later) ===
anchor_blocks = [(0, 2), (2, 10), (8, 10), (8, 4)]
anchor_positions = [(by * 2, bx * 2) for bx, by in anchor_blocks]  # Transposed and converted to feet

# === Trilateration ===
def trilaterate_2D(distances, anchors=anchor_positions, z_tag=Z_TAG):
    anchors = np.array([[x / M_TO_FEET, y / M_TO_FEET, 0] for x, y in anchors])
    x = anchors[:, 0]
    y = anchors[:, 1]
    z = anchors[:, 2]
    kv = x**2 + y**2

    A = np.zeros((NUM_NODES - 1, 2))
    b = np.zeros(NUM_NODES - 1)
    for i in range(1, NUM_NODES):
        A[i-1, 0] = x[i] - x[0]
        A[i-1, 1] = y[i] - y[0]
        b[i-1] = distances[0]**2 - distances[i]**2 + kv[i] - kv[0]

    try:
        Ainv = np.linalg.inv(A.T @ A) @ A.T
        pos = 0.5 * (Ainv @ b)
    except np.linalg.LinAlgError:
        print("[ERROR] Singular matrix, cannot invert.")
        return None, None

    errors = []
    for i in range(NUM_NODES):
        dx = pos[0] - x[i]
        dy = pos[1] - y[i]
        dz = z_tag - z[i]
        estimated_dist = math.sqrt(dx**2 + dy**2 + dz**2)
        errors.append((distances[i] - estimated_dist) ** 2)
    rmse = math.sqrt(sum(errors) / NUM_NODES)

    # Convert to feet
    return pos * M_TO_FEET, rmse * M_TO_FEET

# === Plotting ===
def init_plot():
    plt.ion()
    fig, ax = plt.subplots()
    return fig, ax

def draw_venue(ax, rover_x, rover_y):
    ax.clear()
    block_size = 2
    venue_blocks_w = 6  # Transposed
    venue_blocks_h = 4  # Transposed
    margin_blocks = 3
    total_blocks_w = venue_blocks_w + 2 * margin_blocks
    total_blocks_h = venue_blocks_h + 2 * margin_blocks

    venue_x = margin_blocks * block_size
    venue_y = margin_blocks * block_size
    ax.add_patch(plt.Rectangle(
        (venue_x, venue_y),
        venue_blocks_w * block_size,
        venue_blocks_h * block_size,
        edgecolor='black',
        linewidth=4,
        fill=False
    ))

    for row in range(total_blocks_h + 1):
        y = row * block_size
        ax.plot([0, total_blocks_w * block_size], [y, y], color='lightgray')

    for col in range(total_blocks_w + 1):
        x = col * block_size
        ax.plot([x, x], [0, total_blocks_h * block_size], color='lightgray')

    ax.plot(rover_y, rover_x, 'ro')
    ax.text(rover_y + 0.5, rover_x + 0.5, f"Rover ({rover_x:.2f}, {rover_y:.2f})", color='red')

    for i, (ax_pos, ay_pos) in enumerate(anchor_positions):
        ax.plot(ax_pos, ay_pos, 'bo')
        ax.text(ax_pos + 0.5, ay_pos + 0.5, f"A{i+1}", color='blue')

    ax.set_xlim(-2, total_blocks_w * block_size + 2)
    ax.set_ylim(-2, total_blocks_h * block_size + 2)
    ax.set_aspect('equal')
    ax.set_title("Transposed Venue with Rover and Anchors")
    ax.set_xlabel("Feet (X)")
    ax.set_ylabel("Feet (Y)")
    ax.grid(False)
    plt.gca().invert_yaxis()
    plt.draw()
    plt.pause(0.01)

# === Main Function ===
def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('', PORT))
    print(f"[INFO] Listening for UDP packets on port {PORT}...")

    fig, ax = init_plot()

    while True:
        try:
            data, addr = sock.recvfrom(1024)
            line = data.decode().strip()
            print(f"[RECV] From {addr}: {line}")

            try:
                distances_m = list(map(float, line.split(',')))
            except ValueError:
                print("[ERROR] Could not parse distances.")
                continue

            if len(distances_m) != NUM_NODES:
                print(f"[WARN] Expected {NUM_NODES} distances, got {len(distances_m)}")
                continue

            position, error = trilaterate_2D(distances_m)
            if position is not None:
                print(f"[POS] x = {position[0]:.2f} ft, y = {position[1]:.2f} ft, RMSE = {error:.2f} ft")
                draw_venue(ax, position[1], position[0])
            else:
                print("[FAIL] Position could not be computed.")

        except KeyboardInterrupt:
            print("[EXIT] Interrupted by user.")
            break

if __name__ == "__main__":
    main()
