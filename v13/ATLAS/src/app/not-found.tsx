import Link from 'next/link';

export default function NotFound() {
    return (
        <html lang="en">
            <head>
                <title>ATLAS × QFS — Page Not Found</title>
                <meta name="robots" content="noindex" />
                <link rel="icon" href="./favicon.ico" />
            </head>
            <body
                style={{
                    margin: 0,
                    height: "100vh",
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    background: "radial-gradient(circle at top, #0b1220, #000000)",
                    color: "#e5e7eb",
                    fontFamily:
                        "system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial",
                }}
            >
                <div style={{ textAlign: "center", maxWidth: 520 }}>
                    <img
                        src="./atlas-logo.png"
                        alt="ATLAS × QFS"
                        style={{
                            width: 140,
                            height: "auto",
                            marginBottom: 24,
                            filter: "drop-shadow(0 0 24px rgba(96,165,250,0.35))",
                        }}
                    />

                    <h1
                        style={{
                            fontSize: 42,
                            margin: "0 0 8px",
                            fontWeight: 600,
                            letterSpacing: "-0.02em",
                        }}
                    >
                        404
                    </h1>

                    <p
                        style={{
                            fontSize: 16,
                            opacity: 0.85,
                            marginBottom: 28,
                        }}
                    >
                        This route does not exist in the current ATLAS execution graph.
                    </p>

                    <a
                        href="./index.html"
                        style={{
                            display: "inline-block",
                            padding: "10px 18px",
                            borderRadius: 8,
                            background: "linear-gradient(135deg, #2563eb, #38bdf8)",
                            color: "#ffffff",
                            textDecoration: "none",
                            fontWeight: 500,
                            boxShadow: "0 8px 24px rgba(37,99,235,0.35)",
                        }}
                    >
                        Return to ATLAS
                    </a>

                    <div
                        style={{
                            marginTop: 32,
                            fontSize: 12,
                            opacity: 0.55,
                        }}
                    >
                        ATLAS × QFS · Deterministic Desktop Infrastructure
                    </div>
                </div>
            </body>
        </html>
    );
}
