"""
HTML Dashboard Generator for CALL-E Autonomous Supply Chain Telephony.
Produces an executive-ready, highly intuitive interactive single-page dashboard
showcasing supplier verification calls, KPI metrics, delay analytics,
and conversational transcript drill-downs.
"""

import json
from pathlib import Path
from typing import Optional
from src.models import BatchProcurementReport


def render_html_dashboard(report: BatchProcurementReport, api_base_url: str = "") -> str:
    # Serialize report to JSON for client-side reactivity
    report_dict = report.model_dump()
    report_json_str = json.dumps(report_dict).replace("</script>", "<\\/script>")

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=5.0, viewport-fit=cover" />
  <meta name="theme-color" content="#090d16" id="meta-theme-color" />
  <meta name="apple-mobile-web-app-capable" content="yes" />
  <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent" />
  <title>CALL-E Enterprise Supply Chain Intelligence | Executive Operations Dashboard</title>
  <style>
    :root {{
      --bg-primary: #090d16;
      --bg-secondary: #0f172a;
      --card-bg: #131c31;
      --card-border: #1e293b;
      --card-hover: #1b2640;
      --text-main: #f8fafc;
      --text-muted: #94a3b8;
      --text-dim: #64748b;
      --accent-blue: #3b82f6;
      --accent-indigo: #6366f1;
      --accent-green: #10b981;
      --accent-amber: #f59e0b;
      --accent-red: #ef4444;
      --accent-purple: #8b5cf6;
      --accent-cyan: #06b6d4;
      --font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
      --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.4);
      --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.5), 0 2px 4px -2px rgba(0, 0, 0, 0.5);
      --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.6), 0 4px 6px -4px rgba(0, 0, 0, 0.6);
      --radius-sm: 6px;
      --radius-md: 10px;
      --radius-lg: 16px;
    }}

    body.light-theme {{
      --bg-primary: #f8fafc;
      --bg-secondary: #f1f5f9;
      --card-bg: #ffffff;
      --card-border: #e2e8f0;
      --card-hover: #f8fafc;
      --text-main: #0f172a;
      --text-muted: #475569;
      --text-dim: #94a3b8;
      --shadow-sm: 0 1px 3px rgba(0, 0, 0, 0.08);
      --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
      --shadow-lg: 0 10px 20px -3px rgba(0, 0, 0, 0.1);
    }}

    * {{
      box-sizing: border-box;
      margin: 0;
      padding: 0;
      -webkit-tap-highlight-color: transparent;
    }}

    html, body {{
      max-width: 100%;
      overflow-x: hidden;
    }}

    body {{
      font-family: var(--font-family);
      background-color: var(--bg-primary);
      color: var(--text-main);
      line-height: 1.5;
      min-height: 100vh;
      min-height: 100dvh;
      display: flex;
      flex-direction: column;
      overflow-x: hidden;
      padding-top: env(safe-area-inset-top, 0);
      padding-bottom: env(safe-area-inset-bottom, 0);
    }}

    /* Top Navigation Bar */
    header.top-nav {{
      background-color: var(--bg-secondary);
      border-bottom: 1px solid var(--card-border);
      padding: 0.85rem 1.75rem;
      display: flex;
      align-items: center;
      justify-content: space-between;
      position: sticky;
      top: 0;
      z-index: 40;
      backdrop-filter: blur(12px);
      -webkit-backdrop-filter: blur(12px);
      gap: 1rem;
    }}

    .brand-section {{
      display: flex;
      align-items: center;
      gap: 0.85rem;
      min-width: 0;
      flex-shrink: 1;
    }}

    .brand-icon {{
      width: 40px;
      height: 40px;
      min-width: 40px;
      border-radius: var(--radius-sm);
      background: linear-gradient(135deg, #3b82f6, #6366f1);
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 1.25rem;
      font-weight: 700;
      color: #fff;
      box-shadow: 0 0 15px rgba(99, 102, 241, 0.4);
    }}

    .brand-text {{
      min-width: 0;
    }}

    .brand-text h1 {{
      font-size: 1.15rem;
      font-weight: 700;
      letter-spacing: -0.01em;
      display: flex;
      align-items: center;
      gap: 0.5rem;
      flex-wrap: wrap;
    }}

    .brand-text p {{
      font-size: 0.75rem;
      color: var(--text-muted);
      font-weight: 500;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }}

    .badge-enterprise {{
      background: rgba(59, 130, 246, 0.15);
      color: #60a5fa;
      border: 1px solid rgba(59, 130, 246, 0.3);
      padding: 0.15rem 0.5rem;
      border-radius: 9999px;
      font-size: 0.7rem;
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 0.05em;
    }}

    .nav-actions {{
      display: flex;
      align-items: center;
      gap: 0.75rem;
      flex-shrink: 0;
    }}

    .nav-mobile-bar {{
      display: none;
    }}

    .status-indicator {{
      display: flex;
      align-items: center;
      gap: 0.45rem;
      font-size: 0.8rem;
      color: var(--accent-green);
      font-weight: 600;
      background: rgba(16, 185, 129, 0.1);
      padding: 0.35rem 0.75rem;
      border-radius: 9999px;
      border: 1px solid rgba(16, 185, 129, 0.25);
      white-space: nowrap;
    }}

    .pulse-dot {{
      width: 8px;
      height: 8px;
      border-radius: 50%;
      background-color: var(--accent-green);
      box-shadow: 0 0 8px var(--accent-green);
      animation: pulse 2s infinite ease-in-out;
      flex-shrink: 0;
    }}

    @keyframes pulse {{
      0%, 100% {{ transform: scale(1); opacity: 1; }}
      50% {{ transform: scale(1.3); opacity: 0.6; }}
    }}

    .btn {{
      display: inline-flex;
      align-items: center;
      justify-content: center;
      gap: 0.45rem;
      padding: 0.45rem 0.95rem;
      border-radius: var(--radius-sm);
      font-size: 0.82rem;
      font-weight: 600;
      cursor: pointer;
      transition: all 0.15s ease-in-out;
      border: 1px solid transparent;
      text-decoration: none;
      white-space: nowrap;
      user-select: none;
    }}

    .btn-primary {{
      background: linear-gradient(135deg, #2563eb, #4f46e5);
      color: #fff;
      box-shadow: 0 2px 8px rgba(37, 99, 235, 0.35);
    }}
    .btn-primary:hover {{
      background: linear-gradient(135deg, #1d4ed8, #4338ca);
      transform: translateY(-1px);
    }}

    .btn-secondary {{
      background: var(--card-bg);
      border-color: var(--card-border);
      color: var(--text-main);
    }}
    .btn-secondary:hover {{
      background: var(--card-hover);
      border-color: var(--text-dim);
    }}

    /* Main Container */
    main.dashboard-container {{
      max-width: 1560px;
      width: 100%;
      margin: 0 auto;
      padding: 1.75rem 1.75rem 3rem 1.75rem;
      flex: 1;
      display: flex;
      flex-direction: column;
      gap: 1.5rem;
    }}

    /* Header Summary Banner */
    .summary-banner {{
      background: linear-gradient(135deg, rgba(30, 41, 59, 0.7), rgba(15, 23, 42, 0.9));
      border: 1px solid var(--card-border);
      border-radius: var(--radius-md);
      padding: 1.25rem 1.5rem;
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      justify-content: space-between;
      gap: 1rem;
      box-shadow: var(--shadow-sm);
    }}

    .banner-title h2 {{
      font-size: 1.35rem;
      font-weight: 700;
      letter-spacing: -0.01em;
      margin-bottom: 0.2rem;
    }}

    .banner-title p {{
      color: var(--text-muted);
      font-size: 0.84rem;
    }}

    .banner-meta {{
      display: flex;
      align-items: center;
      gap: 1.25rem;
      font-size: 0.8rem;
      color: var(--text-muted);
    }}

    .banner-meta-item strong {{
      color: var(--text-main);
    }}

    /* KPI Grid */
    .kpi-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(230px, 1fr));
      gap: 1rem;
    }}

    .kpi-card {{
      background-color: var(--card-bg);
      border: 1px solid var(--card-border);
      border-radius: var(--radius-md);
      padding: 1.2rem 1.25rem;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      box-shadow: var(--shadow-sm);
      transition: transform 0.15s ease, border-color 0.15s ease;
      position: relative;
      overflow: hidden;
    }}

    .kpi-card:hover {{
      transform: translateY(-2px);
      border-color: var(--text-dim);
    }}

    .kpi-card::before {{
      content: "";
      position: absolute;
      top: 0;
      left: 0;
      right: 0;
      height: 3px;
      background: var(--kpi-accent, var(--accent-blue));
    }}

    .kpi-header {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      margin-bottom: 0.5rem;
    }}

    .kpi-label {{
      font-size: 0.78rem;
      font-weight: 600;
      color: var(--text-muted);
      text-transform: uppercase;
      letter-spacing: 0.05em;
    }}

    .kpi-icon {{
      width: 28px;
      height: 28px;
      border-radius: var(--radius-sm);
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 0.95rem;
      background: rgba(255, 255, 255, 0.05);
    }}

    .kpi-value {{
      font-size: 1.85rem;
      font-weight: 700;
      letter-spacing: -0.02em;
      line-height: 1.2;
      color: var(--text-main);
      margin-bottom: 0.35rem;
    }}

    .kpi-subtext {{
      font-size: 0.75rem;
      color: var(--text-muted);
      display: flex;
      align-items: center;
      gap: 0.35rem;
    }}

    .trend-pill {{
      display: inline-flex;
      align-items: center;
      gap: 0.2rem;
      padding: 0.1rem 0.4rem;
      border-radius: 9999px;
      font-weight: 600;
      font-size: 0.7rem;
    }}

    .trend-pill.success {{ background: rgba(16, 185, 129, 0.15); color: var(--accent-green); }}
    .trend-pill.warning {{ background: rgba(245, 158, 11, 0.15); color: var(--accent-amber); }}
    .trend-pill.danger {{ background: rgba(239, 68, 68, 0.15); color: var(--accent-red); }}
    .trend-pill.info {{ background: rgba(59, 130, 246, 0.15); color: var(--accent-blue); }}

    /* Analytics & Distribution Row */
    .analytics-row {{
      display: grid;
      grid-template-columns: 1fr 1.5fr;
      gap: 1.25rem;
    }}

    @media (max-width: 1024px) {{
      .analytics-row {{
        grid-template-columns: 1fr;
      }}
    }}

    .chart-panel {{
      background-color: var(--card-bg);
      border: 1px solid var(--card-border);
      border-radius: var(--radius-md);
      padding: 1.25rem;
      box-shadow: var(--shadow-sm);
    }}

    .chart-panel-header {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      margin-bottom: 1rem;
    }}

    .chart-panel-title {{
      font-size: 0.9rem;
      font-weight: 700;
      color: var(--text-main);
      display: flex;
      align-items: center;
      gap: 0.45rem;
    }}

    .chart-panel-desc {{
      font-size: 0.72rem;
      color: var(--text-muted);
    }}

    /* Distribution Bars */
    .bar-list {{
      display: flex;
      flex-direction: column;
      gap: 0.75rem;
    }}

    .bar-item {{
      display: flex;
      flex-direction: column;
      gap: 0.25rem;
    }}

    .bar-label-row {{
      display: flex;
      justify-content: space-between;
      font-size: 0.78rem;
      font-weight: 500;
    }}

    .bar-track {{
      width: 100%;
      height: 8px;
      background-color: rgba(255, 255, 255, 0.07);
      border-radius: 9999px;
      overflow: hidden;
    }}

    .bar-fill {{
      height: 100%;
      border-radius: 9999px;
      transition: width 0.6s ease-out;
    }}

    /* Controls & Filter Bar */
    .controls-bar {{
      background-color: var(--card-bg);
      border: 1px solid var(--card-border);
      border-radius: var(--radius-md);
      padding: 1rem 1.25rem;
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      justify-content: space-between;
      gap: 0.85rem;
      box-shadow: var(--shadow-sm);
    }}

    .search-wrapper {{
      flex: 1;
      min-width: 260px;
      position: relative;
    }}

    .search-input {{
      width: 100%;
      background-color: var(--bg-secondary);
      border: 1px solid var(--card-border);
      border-radius: var(--radius-sm);
      padding: 0.55rem 0.85rem 0.55rem 2.2rem;
      color: var(--text-main);
      font-size: 0.84rem;
      outline: none;
      transition: border-color 0.15s ease;
    }}

    .search-input:focus {{
      border-color: var(--accent-blue);
    }}

    .search-icon {{
      position: absolute;
      left: 0.75rem;
      top: 50%;
      transform: translateY(-50%);
      color: var(--text-dim);
      font-size: 0.85rem;
    }}

    .filters-group {{
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      gap: 0.5rem;
    }}

    .filter-pill {{
      background: var(--bg-secondary);
      border: 1px solid var(--card-border);
      color: var(--text-muted);
      padding: 0.35rem 0.75rem;
      border-radius: 9999px;
      font-size: 0.78rem;
      font-weight: 600;
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      gap: 0.35rem;
      transition: all 0.15s ease;
    }}

    .filter-pill:hover {{
      border-color: var(--text-dim);
      color: var(--text-main);
    }}

    .filter-pill.active {{
      background: var(--accent-blue);
      border-color: var(--accent-blue);
      color: #fff;
    }}

    .filter-pill .pill-count {{
      background: rgba(255, 255, 255, 0.2);
      padding: 0.05rem 0.4rem;
      border-radius: 9999px;
      font-size: 0.7rem;
    }}

    .dropdown-select {{
      background-color: var(--bg-secondary);
      border: 1px solid var(--card-border);
      border-radius: var(--radius-sm);
      padding: 0.45rem 0.75rem;
      color: var(--text-main);
      font-size: 0.8rem;
      outline: none;
      cursor: pointer;
    }}

    .view-toggle {{
      display: flex;
      border: 1px solid var(--card-border);
      border-radius: var(--radius-sm);
      overflow: hidden;
    }}

    .view-btn {{
      background: var(--bg-secondary);
      border: none;
      color: var(--text-muted);
      padding: 0.45rem 0.65rem;
      cursor: pointer;
      font-size: 0.82rem;
      display: flex;
      align-items: center;
      justify-content: center;
    }}

    .view-btn.active {{
      background: var(--accent-blue);
      color: #fff;
    }}

    /* Table View */
    .table-container {{
      background-color: var(--card-bg);
      border: 1px solid var(--card-border);
      border-radius: var(--radius-md);
      overflow: hidden;
      box-shadow: var(--shadow-sm);
    }}

    .table-scroll {{
      overflow-x: auto;
      -webkit-overflow-scrolling: touch;
    }}

    .table-scroll-hint {{
      display: none;
      background: rgba(59, 130, 246, 0.08);
      border-bottom: 1px solid var(--card-border);
      padding: 0.5rem 0.85rem;
      font-size: 0.74rem;
      color: var(--accent-blue);
      align-items: center;
      justify-content: space-between;
    }}

    table.data-table {{
      width: 100%;
      border-collapse: collapse;
      text-align: left;
      font-size: 0.82rem;
    }}

    table.data-table th {{
      background-color: var(--bg-secondary);
      padding: 0.9rem 1rem;
      font-weight: 600;
      color: var(--text-muted);
      text-transform: uppercase;
      font-size: 0.72rem;
      letter-spacing: 0.05em;
      border-bottom: 1px solid var(--card-border);
      white-space: nowrap;
    }}

    table.data-table td {{
      padding: 1.2rem 1rem;
      border-bottom: 1px solid var(--card-border);
      vertical-align: middle;
    }}

    .btn-action-view {{
      display: inline-flex;
      align-items: center;
      gap: 0.35rem;
      padding: 0.32rem 0.65rem;
      font-size: 0.72rem;
      font-weight: 600;
      color: #60a5fa;
      background: rgba(59, 130, 246, 0.1);
      border: 1px solid rgba(59, 130, 246, 0.35);
      border-radius: var(--radius-sm);
      cursor: pointer;
      transition: all 0.15s ease;
      white-space: nowrap;
    }}
    .btn-action-view:hover {{
      background: rgba(59, 130, 246, 0.22);
      border-color: #3b82f6;
      color: #fff;
    }}

    table.data-table tbody tr {{
      transition: background-color 0.1s ease;
      cursor: pointer;
    }}

    table.data-table tbody tr:hover {{
      background-color: var(--card-hover);
    }}

    /* Status Badges */
    .status-badge {{
      display: inline-flex;
      align-items: center;
      gap: 0.35rem;
      padding: 0.2rem 0.6rem;
      border-radius: 9999px;
      font-weight: 600;
      font-size: 0.72rem;
      white-space: nowrap;
      text-transform: uppercase;
      letter-spacing: 0.03em;
    }}

    .status-badge.on-time {{
      background: rgba(16, 185, 129, 0.15);
      color: #34d399;
      border: 1px solid rgba(16, 185, 129, 0.3);
    }}

    .status-badge.delayed {{
      background: rgba(245, 158, 11, 0.15);
      color: #fbbf24;
      border: 1px solid rgba(245, 158, 11, 0.3);
    }}

    .status-badge.partial {{
      background: rgba(59, 130, 246, 0.15);
      color: #60a5fa;
      border: 1px solid rgba(59, 130, 246, 0.3);
    }}

    .status-badge.unreachable {{
      background: rgba(139, 92, 246, 0.15);
      color: #c084fc;
      border: 1px solid rgba(139, 92, 246, 0.3);
    }}

    .escalation-tag {{
      display: inline-flex;
      align-items: center;
      gap: 0.25rem;
      background: rgba(239, 68, 68, 0.18);
      color: #f87171;
      border: 1px solid rgba(239, 68, 68, 0.4);
      padding: 0.1rem 0.45rem;
      border-radius: 9999px;
      font-size: 0.68rem;
      font-weight: 700;
      letter-spacing: 0.04em;
    }}

    /* Card Grid View */
    .cards-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(min(100%, 320px), 1fr));
      gap: 1rem;
    }}

    .call-card {{
      background-color: var(--card-bg);
      border: 1px solid var(--card-border);
      border-radius: var(--radius-md);
      padding: 1.15rem;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      gap: 0.85rem;
      cursor: pointer;
      transition: all 0.15s ease;
      box-shadow: var(--shadow-sm);
    }}

    .call-card:hover {{
      transform: translateY(-2px);
      border-color: var(--text-dim);
      box-shadow: var(--shadow-md);
    }}

    .call-card-top {{
      display: flex;
      align-items: flex-start;
      justify-content: space-between;
      gap: 0.5rem;
    }}

    .card-po {{
      font-weight: 700;
      font-size: 0.95rem;
      color: var(--text-main);
    }}

    .card-supplier {{
      font-weight: 600;
      font-size: 0.85rem;
      color: var(--text-muted);
      margin-top: 0.1rem;
    }}

    .card-item {{
      font-size: 0.8rem;
      color: var(--text-dim);
      line-height: 1.35;
      margin-top: 0.25rem;
    }}

    .card-metrics-row {{
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 0.5rem;
      background: var(--bg-secondary);
      border-radius: var(--radius-sm);
      padding: 0.65rem;
      text-align: center;
    }}

    .card-metric-val {{
      font-weight: 700;
      font-size: 0.85rem;
      color: var(--text-main);
    }}

    .card-metric-lbl {{
      font-size: 0.68rem;
      color: var(--text-muted);
      text-transform: uppercase;
    }}

    .card-footer {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      font-size: 0.75rem;
      color: var(--text-muted);
      border-top: 1px solid var(--card-border);
      padding-top: 0.65rem;
    }}

    /* Modal Styles */
    .modal-overlay {{
      position: fixed;
      inset: 0;
      background: rgba(0, 0, 0, 0.75);
      backdrop-filter: blur(8px);
      display: none;
      align-items: center;
      justify-content: center;
      z-index: 100;
      padding: 1.5rem;
    }}

    .modal-overlay.active {{
      display: flex;
    }}

    .modal-dialog {{
      background: var(--card-bg);
      border: 1px solid var(--card-border);
      border-radius: var(--radius-lg);
      width: 100%;
      max-width: 900px;
      max-height: 90vh;
      display: flex;
      flex-direction: column;
      overflow: hidden;
      box-shadow: var(--shadow-lg);
      animation: modalPop 0.2s cubic-bezier(0.16, 1, 0.3, 1);
    }}

    @keyframes modalPop {{
      0% {{ transform: scale(0.96); opacity: 0; }}
      100% {{ transform: scale(1); opacity: 1; }}
    }}

    .modal-header {{
      padding: 1.25rem 1.5rem;
      border-bottom: 1px solid var(--card-border);
      display: flex;
      align-items: center;
      justify-content: space-between;
      background: var(--bg-secondary);
    }}

    .modal-title h3 {{
      font-size: 1.15rem;
      font-weight: 700;
      display: flex;
      align-items: center;
      gap: 0.5rem;
    }}

    .modal-close {{
      background: transparent;
      border: none;
      color: var(--text-muted);
      font-size: 1.4rem;
      cursor: pointer;
      padding: 0.25rem 0.5rem;
      border-radius: var(--radius-sm);
    }}
    .modal-close:hover {{
      color: var(--text-main);
      background: rgba(255, 255, 255, 0.08);
    }}

    .modal-body {{
      padding: 1.5rem;
      overflow-y: auto;
      display: flex;
      flex-direction: column;
      gap: 1.25rem;
    }}

    /* Transcript Chat Bubbles with High Contrast */
    .transcript-box {{
      background: #0b1120;
      border: 1px solid var(--card-border);
      border-radius: var(--radius-md);
      padding: 1.25rem;
      display: flex;
      flex-direction: column;
      gap: 1rem;
      max-height: 380px;
      overflow-y: auto;
    }}

    .chat-bubble {{
      display: flex;
      flex-direction: column;
      max-width: 84%;
      padding: 0.85rem 1.15rem;
      border-radius: var(--radius-md);
      font-size: 0.86rem;
      line-height: 1.5;
      position: relative;
    }}

    .chat-bubble.agent {{
      align-self: flex-start;
      background-color: #1e293b;
      border: 1px solid rgba(148, 163, 184, 0.28);
      color: #f8fafc;
      border-bottom-left-radius: 2px;
      box-shadow: 0 2px 4px rgba(0, 0, 0, 0.25);
    }}

    .chat-bubble.supplier {{
      align-self: flex-end;
      background-color: #1d4ed8;
      border: 1px solid #3b82f6;
      color: #ffffff;
      border-bottom-right-radius: 2px;
      box-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
    }}

    body.light-theme .chat-bubble.agent {{
      background-color: #f1f5f9;
      border: 1px solid #cbd5e1;
      color: #0f172a;
    }}

    body.light-theme .chat-bubble.supplier {{
      background-color: #dbeafe;
      border: 1px solid #93c5fd;
      color: #1e3a8a;
    }}

    .speaker-name {{
      font-size: 0.7rem;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      margin-bottom: 0.25rem;
      display: flex;
      align-items: center;
      gap: 0.35rem;
    }}

    .speaker-name.agent-lbl {{ color: #60a5fa; }}
    .speaker-name.supplier-lbl {{ color: #bfdbfe; }}

    .entity-tag {{
      display: inline-block;
      background: rgba(245, 158, 11, 0.2);
      border: 1px solid rgba(245, 158, 11, 0.4);
      color: #fef08a;
      padding: 0.05rem 0.35rem;
      border-radius: 4px;
      font-weight: 600;
      font-size: 0.78rem;
    }}

    /* Trigger Call Form Modal */
    .form-group {{
      display: flex;
      flex-direction: column;
      gap: 0.35rem;
    }}

    .form-label {{
      font-size: 0.78rem;
      font-weight: 600;
      color: var(--text-muted);
      display: flex;
      align-items: center;
      gap: 0.35rem;
    }}

    .form-input, .form-select {{
      background-color: var(--bg-secondary);
      border: 1px solid var(--card-border);
      border-radius: var(--radius-sm);
      padding: 0.6rem 0.9rem;
      color: var(--text-main);
      font-size: 0.84rem;
      outline: none;
      transition: border-color 0.15s ease, box-shadow 0.15s ease;
    }}

    .form-select {{
      appearance: none;
      -webkit-appearance: none;
      -moz-appearance: none;
      background-image: url("data:image/svg+xml;charset=UTF-8,%3csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%2394a3b8' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3e%3cpolyline points='6 9 12 15 18 9'%3e%3c/polyline%3e%3c/svg%3e");
      background-repeat: no-repeat;
      background-position: right 0.85rem center;
      background-size: 1rem;
      padding-right: 2.3rem;
      cursor: pointer;
    }}

    .form-input:focus, .form-select:focus {{
      border-color: var(--accent-blue);
      box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.2);
    }}

    /* Read-Only Informational Inputs */
    .form-input-readonly, .form-input[readonly] {{
      background-color: rgba(15, 23, 42, 0.55) !important;
      border: 1px dashed rgba(148, 163, 184, 0.25) !important;
      color: #94a3b8 !important;
      cursor: default;
      user-select: none;
    }}
    .form-input-readonly:focus, .form-input[readonly]:focus {{
      border-color: rgba(148, 163, 184, 0.35) !important;
      box-shadow: none !important;
    }}

    /* Editable Destination Phone Input */
    .form-input-editable {{
      border: 1.5px solid var(--accent-blue) !important;
      background-color: rgba(59, 130, 246, 0.05) !important;
    }}

    .badge-readonly {{
      font-size: 0.65rem;
      font-weight: 500;
      color: var(--text-dim);
      background: rgba(255, 255, 255, 0.06);
      padding: 1px 6px;
      border-radius: 4px;
      text-transform: uppercase;
      letter-spacing: 0.04em;
    }}

    .badge-editable {{
      font-size: 0.65rem;
      font-weight: 600;
      color: #60a5fa;
      background: rgba(59, 130, 246, 0.15);
      padding: 1px 6px;
      border-radius: 4px;
      text-transform: uppercase;
      letter-spacing: 0.04em;
    }}

    .form-grid-2 {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 1rem;
    }}

    .telephony-banner {{
      padding: 0.75rem 1rem;
      border-radius: var(--radius-sm);
      font-size: 0.78rem;
      line-height: 1.45;
    }}
    .telephony-banner.warning {{
      background: rgba(245, 158, 11, 0.12);
      border: 1px solid rgba(245, 158, 11, 0.35);
      color: #fbbf24;
    }}
    .telephony-banner.ready {{
      background: rgba(16, 185, 129, 0.12);
      border: 1px solid rgba(16, 185, 129, 0.35);
      color: #34d399;
    }}

    .execution-summary-bar {{
      background: var(--bg-secondary);
      border: 1px solid var(--card-border);
      border-radius: var(--radius-sm);
      padding: 0.75rem 1rem;
      display: flex;
      justify-content: space-between;
      align-items: center;
      flex-wrap: wrap;
      gap: 0.5rem;
    }}

    .call-error-box {{
      background: rgba(239, 68, 68, 0.08);
      border: 1px solid rgba(239, 68, 68, 0.35);
      border-radius: var(--radius-md);
      padding: 1rem;
      display: flex;
      flex-direction: column;
      gap: 0.75rem;
    }}

    .call-outcome-box {{
      background: var(--bg-secondary);
      border: 1px solid var(--card-border);
      border-radius: var(--radius-md);
      padding: 1rem;
      display: flex;
      flex-direction: column;
      gap: 0.75rem;
    }}

    /* =========================================================
       RESPONSIVE DESIGN & MOBILE LAYOUT PATTERNS (BEST PRACTICES)
       ========================================================= */

    /* Tablet & Medium Screens */
    @media (max-width: 1024px) {{
      main.dashboard-container {{
        padding: 1.25rem 1.25rem 2.5rem 1.25rem;
        gap: 1.25rem;
      }}
      .kpi-grid {{
        grid-template-columns: repeat(3, 1fr);
        gap: 0.85rem;
      }}
      .analytics-row {{
        grid-template-columns: 1fr;
        gap: 1rem;
      }}
    }}

    /* Mobile Screens (Landscape & Large Phones <= 900px) */
    @media (max-width: 900px) {{
      header.top-nav {{
        padding: 0.75rem 1rem;
        flex-wrap: wrap;
        gap: 0.5rem;
      }}

      .brand-text p {{
        display: none;
      }}

      .brand-text h1 {{
        font-size: 1rem;
      }}

      .nav-mobile-bar {{
        display: flex;
        align-items: center;
        gap: 0.45rem;
      }}

      .nav-desktop-call-btn,
      .nav-desktop-theme-btn {{
        display: none;
      }}

      .nav-actions {{
        display: none;
        width: 100%;
        flex-direction: column;
        align-items: stretch;
        gap: 0.6rem;
        padding: 0.75rem 0 0.25rem 0;
        border-top: 1px solid var(--card-border);
      }}

      .nav-actions.is-open {{
        display: flex;
      }}

      .nav-actions .status-indicator {{
        width: 100%;
        justify-content: center;
      }}

      .nav-actions .btn {{
        width: 100%;
        min-height: 42px;
        font-size: 0.85rem;
      }}
    }}

    /* Mobile Phones (<= 768px) */
    @media (max-width: 768px) {{
      main.dashboard-container {{
        padding: 0.85rem 0.75rem 2rem 0.75rem;
        gap: 0.85rem;
      }}

      /* Summary Banner Mobile Grid */
      .summary-banner {{
        padding: 1rem;
        gap: 0.75rem;
      }}

      .banner-title h2 {{
        font-size: 1.15rem;
      }}

      .banner-title p {{
        font-size: 0.78rem;
      }}

      .banner-meta {{
        display: grid;
        grid-template-columns: repeat(2, 1fr);
        gap: 0.5rem;
        width: 100%;
      }}

      .banner-meta-item {{
        background: rgba(15, 23, 42, 0.6);
        padding: 0.45rem 0.6rem;
        border-radius: var(--radius-sm);
        border: 1px solid rgba(255, 255, 255, 0.05);
        font-size: 0.74rem;
      }}

      /* KPI Cards 2-Column Mobile Grid Pattern */
      .kpi-grid {{
        grid-template-columns: repeat(2, 1fr);
        gap: 0.65rem;
      }}

      .kpi-card {{
        padding: 0.85rem 0.75rem;
      }}

      .kpi-label {{
        font-size: 0.68rem;
      }}

      .kpi-icon {{
        width: 24px;
        height: 24px;
        font-size: 0.85rem;
      }}

      .kpi-value {{
        font-size: 1.35rem;
        margin-bottom: 0.25rem;
      }}

      .kpi-subtext {{
        font-size: 0.68rem;
        flex-wrap: wrap;
        gap: 0.2rem;
      }}

      .trend-pill {{
        font-size: 0.62rem;
        padding: 0.05rem 0.35rem;
      }}

      /* Analytics Chart Panel Mobile Styling */
      .chart-panel {{
        padding: 1rem 0.85rem;
      }}

      .chart-panel-title {{
        font-size: 0.85rem;
      }}

      .chart-panel-desc {{
        font-size: 0.7rem;
      }}

      .bar-label-row {{
        font-size: 0.75rem;
        flex-wrap: wrap;
        gap: 0.25rem 0.5rem;
      }}

      /* Controls Bar Mobile Stack & Horizontal Chip Scroll */
      .controls-bar {{
        flex-direction: column;
        align-items: stretch;
        padding: 0.85rem;
        gap: 0.75rem;
      }}

      .search-wrapper {{
        min-width: 0;
        width: 100%;
      }}

      .search-input {{
        font-size: 16px; /* Prevents mobile Safari auto-zoom */
        padding: 0.65rem 0.85rem 0.65rem 2.2rem;
        min-height: 42px;
      }}

      #status-filter-pills {{
        display: flex;
        flex-wrap: nowrap;
        overflow-x: auto;
        -webkit-overflow-scrolling: touch;
        scrollbar-width: none;
        gap: 0.4rem;
        padding: 0.15rem 0.15rem 0.4rem 0.15rem;
        margin: 0 -0.15rem;
      }}

      #status-filter-pills::-webkit-scrollbar {{
        display: none;
      }}

      .filter-pill {{
        flex-shrink: 0;
        white-space: nowrap;
        padding: 0.4rem 0.75rem;
        font-size: 0.78rem;
        min-height: 36px;
      }}

      .controls-actions-group {{
        display: grid;
        grid-template-columns: 1fr 1fr auto;
        width: 100%;
        gap: 0.5rem;
        align-items: center;
      }}

      .dropdown-select {{
        font-size: 14px;
        min-height: 40px;
        width: 100%;
      }}

      .view-toggle {{
        min-height: 40px;
      }}

      .view-btn {{
        min-width: 40px;
        min-height: 40px;
      }}

      /* Table View Mobile Hint & Scroll Touch */
      .table-scroll-hint {{
        display: flex;
      }}

      table.data-table th {{
        padding: 0.65rem 0.6rem;
        font-size: 0.68rem;
      }}

      table.data-table td {{
        padding: 0.75rem 0.6rem;
      }}

      /* Cards Grid View Mobile */
      .cards-grid {{
        grid-template-columns: 1fr;
        gap: 0.85rem;
      }}

      .call-card {{
        padding: 1rem;
      }}

      .card-footer {{
        flex-direction: column;
        align-items: stretch;
        gap: 0.65rem;
      }}

      .card-footer-actions {{
        display: flex;
        gap: 0.5rem;
        width: 100%;
      }}

      .card-footer-actions .btn-action-view,
      .card-footer-actions .btn {{
        flex: 1;
        justify-content: center;
        min-height: 40px;
        font-size: 0.8rem;
      }}

      /* Footer */
      footer.app-footer {{
        flex-direction: column;
        text-align: center;
        gap: 0.4rem;
        padding: 1rem 0.75rem;
        font-size: 0.74rem;
      }}
    }}

    /* Narrow Mobile Phones (<= 640px) */
    @media (max-width: 640px) {{
      /* Modal Mobile Bottom-Sheet Pattern */
      .modal-overlay {{
        padding: 0;
        align-items: flex-end;
      }}

      .modal-dialog {{
        border-radius: var(--radius-lg) var(--radius-lg) 0 0;
        max-height: 94vh;
        max-height: 94dvh;
        width: 100%;
        margin: 0;
        animation: modalSlideUp 0.25s cubic-bezier(0.16, 1, 0.3, 1);
      }}

      @keyframes modalSlideUp {{
        0% {{ transform: translateY(100%); opacity: 0; }}
        100% {{ transform: translateY(0); opacity: 1; }}
      }}

      .modal-header {{
        padding: 1rem 1.15rem;
      }}

      .modal-title h3 {{
        font-size: 1rem;
      }}

      .modal-close {{
        width: 44px;
        height: 44px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.5rem;
      }}

      .modal-body {{
        padding: 1rem 1.15rem 1.75rem 1.15rem;
        gap: 1rem;
        -webkit-overflow-scrolling: touch;
      }}

      /* Collapse side-by-side form grid to 1-column on mobile */
      .form-grid-2 {{
        grid-template-columns: 1fr;
        gap: 0.85rem;
      }}

      .form-input, .form-select {{
        font-size: 16px; /* Prevents auto-zoom on iOS */
        padding: 0.65rem 0.85rem;
        min-height: 44px;
      }}

      .modal-overview-grid {{
        grid-template-columns: repeat(2, 1fr) !important;
        gap: 0.5rem !important;
      }}

      .outcome-findings-grid {{
        grid-template-columns: repeat(2, 1fr) !important;
        gap: 0.5rem !important;
      }}

      .modal-actions-row {{
        flex-direction: column-reverse;
        gap: 0.5rem;
        width: 100%;
      }}

      .modal-actions-row .btn {{
        width: 100%;
        min-height: 44px;
        font-size: 0.88rem;
      }}

      .chat-bubble {{
        max-width: 92%;
        padding: 0.75rem 0.95rem;
        font-size: 0.82rem;
      }}

      .call-error-box .btn,
      .call-outcome-box .btn {{
        width: 100%;
        min-height: 42px;
      }}
    }}

    /* Very Small Phones (<= 480px) */
    @media (max-width: 480px) {{
      .controls-actions-group {{
        grid-template-columns: 1fr 1fr;
      }}

      .controls-actions-group .view-toggle {{
        grid-column: 1 / -1;
        display: flex;
        width: 100%;
      }}

      .controls-actions-group .view-toggle .view-btn {{
        flex: 1;
        padding: 0.5rem;
      }}

      .card-metrics-row {{
        padding: 0.5rem;
        gap: 0.25rem;
      }}

      .card-metric-val {{
        font-size: 0.78rem;
      }}

      .card-metric-lbl {{
        font-size: 0.64rem;
      }}
    }}

    /* Ultra Small Phones (<= 360px) */
    @media (max-width: 360px) {{
      .kpi-grid {{
        grid-template-columns: 1fr;
      }}

      .banner-meta {{
        grid-template-columns: 1fr;
      }}

      .modal-overview-grid {{
        grid-template-columns: 1fr !important;
      }}

      .outcome-findings-grid {{
        grid-template-columns: 1fr !important;
      }}
    }}

    /* Reusable Shimmer Animation for API Calls and Data Loading States */
    @keyframes shimmerWave {{
      0% {{ background-position: -200% 0; }}
      100% {{ background-position: 200% 0; }}
    }}
    .skeleton-shimmer {{
      background: linear-gradient(90deg, rgba(255, 255, 255, 0.04) 25%, rgba(255, 255, 255, 0.12) 37%, rgba(255, 255, 255, 0.04) 63%);
      background-size: 200% 100%;
      animation: shimmerWave 1.4s ease-in-out infinite;
      border-radius: 6px;
      display: inline-block;
    }}
    .skeleton-bar {{
      height: 14px;
      width: 100%;
    }}
    .skeleton-bar-sm {{
      height: 10px;
      width: 60%;
    }}
    .skeleton-pill {{
      height: 22px;
      width: 70px;
      border-radius: 12px;
    }}

    /* Print styling */
    @media print {{
      header.top-nav, .controls-bar, .nav-actions, .modal-overlay, footer {{
        display: none !important;
      }}
      body {{
        background: #fff !important;
        color: #000 !important;
      }}
      .kpi-card, .chart-panel, .table-container {{
        border: 1px solid #ccc !important;
        background: #fff !important;
        color: #000 !important;
        box-shadow: none !important;
      }}
    }}
  </style>
</head>
<body>

  <!-- Top Navigation Bar -->
  <header class="top-nav">
    <div class="brand-section">
      <div class="brand-icon">📞</div>
      <div class="brand-text">
        <h1>
          CALL-E Supply Chain Intelligence
          <span class="badge-enterprise">Enterprise Control Tower</span>
        </h1>
        <p>Autonomous Voice Telephony & Vendor Fulfillment Verification Network</p>
      </div>
    </div>

    <!-- Mobile Quick Bar (visible on mobile screens <= 900px) -->
    <div class="nav-mobile-bar">
      <button class="btn btn-primary nav-mobile-call-btn" onclick="openNewCallModal()" title="Trigger Verification Call">
        <span>📞</span> <span class="nav-mobile-call-text">Call</span>
      </button>
      <button class="btn btn-secondary nav-mobile-theme-btn" onclick="toggleTheme()" title="Toggle Dark/Light Mode">
        <span id="theme-icon-mobile">☀️</span>
      </button>
      <button class="btn btn-secondary nav-mobile-menu-btn" id="mobile-menu-btn" onclick="toggleMobileMenu()" aria-label="Toggle Navigation Menu">
        <span id="mobile-menu-icon">☰</span>
      </button>
    </div>

    <div class="nav-actions" id="nav-actions-menu">
      <div class="status-indicator" id="backend-status-indicator" title="Connection status to VPS FastAPI backend">
        <span class="pulse-dot" id="backend-pulse-dot"></span>
        <span id="backend-status-text">FastAPI Backend: Connecting...</span>
      </div>
      <button class="btn btn-secondary" onclick="syncWithBackend(true)" title="Fetch latest calls and KPIs directly from Python SQLite database">
        <span>🔄</span> Sync Data
      </button>
      <button class="btn btn-primary nav-desktop-call-btn" onclick="openNewCallModal()">
        <span>📞</span> Trigger Verification Call
      </button>
      <button class="btn btn-secondary" onclick="exportFilteredCSV()">
        <span>📥</span> Export CSV
      </button>
      <button class="btn btn-secondary" onclick="exportFilteredJSON()">
        <span>📋</span> Export JSON
      </button>
      <button class="btn btn-secondary nav-desktop-theme-btn" onclick="toggleTheme()" title="Toggle Dark/Light Mode">
        <span id="theme-icon">☀️</span>
      </button>
    </div>
  </header>

  <!-- Main Dashboard Container -->
  <main class="dashboard-container">

    <!-- Executive Summary Banner -->
    <section class="summary-banner">
      <div class="banner-title">
        <h2>Global Procurement Fulfillment Summary</h2>
        <p>Continuous AI autonomous monitoring across Tier-1 and Tier-2 critical supply lines</p>
      </div>
      <div class="banner-meta">
        <div class="banner-meta-item">Report ID: <strong id="rep-id">{report.report_id}</strong></div>
        <div class="banner-meta-item">Monitored Vendors: <strong id="vendor-count">{report.total_orders_checked}</strong></div>
        <div class="banner-meta-item">Calculated Risk: <strong id="total-risk-val">${report.total_financial_risk_usd:,.2f}</strong></div>
        <div class="banner-meta-item">Updated: <strong>{report.generated_at[:19].replace('T', ' ')} UTC</strong></div>
      </div>
    </section>

    <!-- Executive KPI Cards -->
    <section class="kpi-grid">
      <!-- KPI 1 -->
      <div class="kpi-card" style="--kpi-accent: var(--accent-blue);">
        <div class="kpi-header">
          <span class="kpi-label">Total Calls Executed</span>
          <span class="kpi-icon">📦</span>
        </div>
        <div class="kpi-value" id="kpi-total-orders">{report.total_orders_checked}</div>
        <div class="kpi-subtext">
          <span class="trend-pill info">100% Verified</span>
          <span>outbound voice runs</span>
        </div>
      </div>

      <!-- KPI 2 -->
      <div class="kpi-card" style="--kpi-accent: var(--accent-green);">
        <div class="kpi-header">
          <span class="kpi-label">On-Time Fulfillment Rate</span>
          <span class="kpi-icon">✅</span>
        </div>
        <div class="kpi-value" id="kpi-on-time-pct">{report.on_time_percentage}%</div>
        <div class="kpi-subtext">
          <span class="trend-pill success"><span id="kpi-on-time-cnt">{report.on_time_count}</span> Orders</span>
          <span>confirmed on schedule</span>
        </div>
      </div>

      <!-- KPI 3 -->
      <div class="kpi-card" style="--kpi-accent: var(--accent-amber);">
        <div class="kpi-header">
          <span class="kpi-label">Delayed / At-Risk Shipments</span>
          <span class="kpi-icon">⚠️</span>
        </div>
        <div class="kpi-value" id="kpi-delayed-cnt">{report.delayed_count}</div>
        <div class="kpi-subtext">
          <span class="trend-pill warning">Disruptions</span>
          <span>schedule revisions captured</span>
        </div>
      </div>

      <!-- KPI 4 -->
      <div class="kpi-card" style="--kpi-accent: var(--accent-red);">
        <div class="kpi-header">
          <span class="kpi-label">Total Financial Exposure</span>
          <span class="kpi-icon">💰</span>
        </div>
        <div class="kpi-value" id="kpi-financial-risk">${report.total_financial_risk_usd:,.0f}</div>
        <div class="kpi-subtext">
          <span class="trend-pill danger">Penalties + Expedite</span>
          <span>quantified real-time</span>
        </div>
      </div>

      <!-- KPI 5 -->
      <div class="kpi-card" style="--kpi-accent: var(--accent-purple);">
        <div class="kpi-header">
          <span class="kpi-label">Critical Escalations</span>
          <span class="kpi-icon">🚨</span>
        </div>
        <div class="kpi-value" id="kpi-escalations-cnt">{len(report.critical_escalations)}</div>
        <div class="kpi-subtext">
          <span class="trend-pill danger">Action Required</span>
          <span>VP / Director tier</span>
        </div>
      </div>

      <!-- KPI 6 -->
      <div class="kpi-card" style="--kpi-accent: var(--accent-cyan);">
        <div class="kpi-header">
          <span class="kpi-label">Voice Hours Saved</span>
          <span class="kpi-icon">⏱️</span>
        </div>
        <div class="kpi-value" id="kpi-hours-saved">{(report.total_orders_checked * 0.35):.1f}h</div>
        <div class="kpi-subtext">
          <span class="trend-pill success">Autonomous</span>
          <span>zero manual dial overhead</span>
        </div>
      </div>
    </section>

    <!-- Analytics & Distribution Row -->
    <section class="analytics-row">
      <!-- Fulfillment Breakdown -->
      <div class="chart-panel">
        <div class="chart-panel-header">
          <div>
            <div class="chart-panel-title"><span>📊</span> Fulfillment Status Breakdown</div>
            <div class="chart-panel-desc">Real-time status distribution across all purchase orders</div>
          </div>
        </div>
        <div class="bar-list" id="status-distribution-bars">
          <!-- Dynamically populated -->
        </div>
      </div>

      <!-- Delay Root Causes & Financial Risk (Consolidated Widget) -->
      <div class="chart-panel consolidated-panel">
        <div class="chart-panel-header">
          <div>
            <div class="chart-panel-title"><span>🛡️</span> Delay Root Causes & Financial Exposure</div>
            <div class="chart-panel-desc">Consolidated operational disruption taxonomy with quantified financial penalty risk side-by-side</div>
          </div>
        </div>
        <div class="bar-list" id="delay-category-bars">
          <!-- Dynamically populated with count + financial risk side-by-side -->
        </div>
        <div id="risk-category-bars" style="display: none;"></div>
      </div>
    </section>

    <!-- Search & Filter Controls -->
    <section class="controls-bar">
      <div class="search-wrapper">
        <span class="search-icon">🔍</span>
        <input
          type="text"
          id="search-input"
          class="search-input"
          placeholder="Search by PO #, Supplier, Contact, Phone (+1-563...), or Call ID..."
          oninput="applyFilters()"
        />
      </div>

      <div class="filters-group" id="status-filter-pills">
        <button class="filter-pill active" onclick="setStatusFilter('ALL')">
          All <span class="pill-count" id="pill-count-all">0</span>
        </button>
        <button class="filter-pill" onclick="setStatusFilter('ON_TIME')">
          On-Time <span class="pill-count" id="pill-count-ontime">0</span>
        </button>
        <button class="filter-pill" onclick="setStatusFilter('DELAYED')">
          Delayed <span class="pill-count" id="pill-count-delayed">0</span>
        </button>
        <button class="filter-pill" onclick="setStatusFilter('PARTIAL_DISPATCH')">
          Partial <span class="pill-count" id="pill-count-partial">0</span>
        </button>
        <button class="filter-pill" onclick="setStatusFilter('UNREACHABLE')">
          Unreachable <span class="pill-count" id="pill-count-unreachable">0</span>
        </button>
        <button class="filter-pill" onclick="setStatusFilter('ESCALATION')">
          🚨 Escalations Only <span class="pill-count" id="pill-count-escalations">0</span>
        </button>
      </div>

      <div class="filters-group controls-actions-group">
        <select id="category-filter" class="dropdown-select" onchange="applyFilters()">
          <option value="ALL">All Categories</option>
        </select>

        <select id="sort-filter" class="dropdown-select" onchange="applyFilters()">
          <option value="RISK_DESC">Highest Financial Risk</option>
          <option value="DELAY_DESC">Longest Delay First</option>
          <option value="DATE_ASC">Committed Date (Earliest)</option>
          <option value="SUPPLIER_ASC">Supplier Name (A-Z)</option>
        </select>

        <div class="view-toggle">
          <button id="btn-view-table" class="view-btn active" onclick="setViewMode('table')" title="Table View">☰</button>
          <button id="btn-view-cards" class="view-btn" onclick="setViewMode('cards')" title="Grid Cards View">☷</button>
        </div>
      </div>
    </section>

    <!-- Table View -->
    <section id="table-view-section" class="table-container">
      <div class="table-scroll-hint">
        <span>↔ Scroll horizontally to view full ledger</span>
        <span>Tip: Switch to ☷ Cards for mobile view</span>
      </div>
      <div class="table-scroll">
        <table class="data-table">
          <thead>
            <tr>
              <th>Status</th>
              <th>PO Number</th>
              <th>Supplier</th>
              <th>Item & Quantity</th>
              <th>Committed</th>
              <th>Revised Date</th>
              <th>Delay</th>
              <th>Root Cause</th>
              <th>Financial Risk</th>
              <th>Escalation Lead</th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody id="calls-table-body">
            <!-- Dynamically populated -->
          </tbody>
        </table>
      </div>
    </section>

    <!-- Card Grid View -->
    <section id="cards-view-section" class="cards-grid" style="display: none;">
      <!-- Dynamically populated -->
    </section>

  </main>

  <!-- Call Details & Transcript Modal -->
  <div id="call-modal" class="modal-overlay" onclick="handleModalBackdropClick(event)">
    <div class="modal-dialog">
      <div class="modal-header">
        <div class="modal-title">
          <h3 id="modal-po-header">PO Details & Call Transcript</h3>
        </div>
        <button class="modal-close" onclick="closeCallModal()">✕</button>
      </div>

      <div class="modal-body">
        <!-- Call Overview Grid -->
        <div class="modal-overview-grid" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 0.75rem;">
          <div style="background: var(--bg-secondary); padding: 0.75rem; border-radius: var(--radius-sm);">
            <div style="font-size: 0.7rem; color: var(--text-muted); text-transform: uppercase;">Call ID</div>
            <div id="modal-call-id" style="font-weight: 700; font-size: 0.85rem; font-family: monospace;"></div>
          </div>
          <div style="background: var(--bg-secondary); padding: 0.75rem; border-radius: var(--radius-sm);">
            <div style="font-size: 0.7rem; color: var(--text-muted); text-transform: uppercase;">Supplier Contact</div>
            <div id="modal-contact-name" style="font-weight: 600; font-size: 0.85rem;"></div>
          </div>
          <div style="background: var(--bg-secondary); padding: 0.75rem; border-radius: var(--radius-sm);">
            <div style="font-size: 0.7rem; color: var(--text-muted); text-transform: uppercase;">Phone Number</div>
            <div id="modal-phone" style="font-weight: 600; font-size: 0.85rem; font-family: monospace;"></div>
          </div>
          <div style="background: var(--bg-secondary); padding: 0.75rem; border-radius: var(--radius-sm);">
            <div style="font-size: 0.7rem; color: var(--text-muted); text-transform: uppercase;">Call Duration</div>
            <div id="modal-duration" style="font-weight: 600; font-size: 0.85rem;"></div>
          </div>
        </div>

        <!-- Financial Impact Box -->
        <div style="background: linear-gradient(135deg, rgba(239, 68, 68, 0.1), rgba(245, 158, 11, 0.1)); border: 1px solid rgba(239, 68, 68, 0.3); border-radius: var(--radius-md); padding: 1rem; display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 0.5rem;">
          <div>
            <div style="font-size: 0.75rem; font-weight: 700; text-transform: uppercase; color: #f87171;">Supply Chain Risk Quantification</div>
            <div id="modal-risk-formula" style="font-size: 0.82rem; color: var(--text-muted); margin-top: 0.2rem;"></div>
          </div>
          <div id="modal-total-impact" style="font-size: 1.4rem; font-weight: 800; color: #fca5a5;"></div>
        </div>

        <!-- Escalation Contact Card -->
        <div id="modal-escalation-card" style="background: var(--bg-secondary); border: 1px solid var(--card-border); border-radius: var(--radius-md); padding: 0.85rem 1.15rem; display: flex; align-items: center; justify-content: space-between;">
          <div style="display: flex; align-items: center; gap: 0.75rem;">
            <span style="font-size: 1.3rem;">🚨</span>
            <div>
              <div style="font-size: 0.72rem; color: var(--text-muted); text-transform: uppercase; font-weight: 700;">Designated Escalation Officer</div>
              <div id="modal-esc-name" style="font-weight: 700; font-size: 0.88rem; color: var(--text-main);"></div>
            </div>
          </div>
          <div id="modal-esc-phone" style="font-family: monospace; font-size: 0.85rem; font-weight: 600; color: var(--accent-blue);"></div>
        </div>

        <!-- Structured Dialogue Transcript -->
        <div>
          <div style="font-size: 0.82rem; font-weight: 700; color: var(--text-muted); margin-bottom: 0.5rem; text-transform: uppercase; letter-spacing: 0.04em; display: flex; align-items: center; gap: 0.4rem;">
            <span>💬</span> Verified Conversational Dialogue Transcript
          </div>
          <div class="transcript-box" id="modal-transcript-container">
            <!-- Bubbles rendered dynamically -->
          </div>
        </div>
      </div>
    </div>
  </div>

  <!-- Trigger New Outbound Call Modal -->
  <div id="new-call-modal" class="modal-overlay" onclick="handleNewCallBackdropClick(event)">
    <div class="modal-dialog" style="max-width: 620px;">
      <div class="modal-header">
        <div class="modal-title">
          <h3 id="new-call-modal-title"><span>📞</span> Trigger Autonomous Outbound Call</h3>
        </div>
        <button class="modal-close" onclick="closeNewCallModal()">✕</button>
      </div>

      <div class="modal-body">
        <!-- Telephony Readiness Notice Banner -->
        <div id="server-telephony-banner" class="telephony-banner ready" style="display: none; margin-bottom: 1rem;">
          <!-- Dynamically populated based on server /health status -->
        </div>

        <!-- VIEW 1: Call Configuration Form -->
        <div id="new-call-form-view">
          <form id="new-call-form" onsubmit="executeManualCall(event)" style="display: flex; flex-direction: column; gap: 1rem;">
            <div class="form-group">
              <label class="form-label">Select Target Supplier</label>
              <select id="form-supplier-select" class="form-select" onchange="populateSupplierFields()">
                <!-- Populated dynamically -->
              </select>
            </div>

            <div class="form-grid-2">
              <div class="form-group">
                <label class="form-label">Purchase Order ID <span class="badge-readonly">Auto-Populated</span></label>
                <input type="text" id="form-po-id" class="form-input form-input-readonly" readonly required value="PO-99500" />
              </div>
              <div class="form-group">
                <label class="form-label">Committed Delivery Date <span class="badge-readonly">Auto-Populated</span></label>
                <input type="date" id="form-delivery-date" class="form-input form-input-readonly" readonly required value="2026-09-25" />
              </div>
            </div>

            <div class="form-grid-2">
              <div class="form-group">
                <label class="form-label">Supplier Contact Name <span class="badge-readonly">Auto-Populated</span></label>
                <input type="text" id="form-contact-name" class="form-input form-input-readonly" readonly required placeholder="e.g. Sandra Bullock" />
              </div>
              <div class="form-group">
                <label class="form-label">Supplier Phone Number <span class="badge-editable">Editable Destination</span></label>
                <input type="text" id="form-phone" class="form-input form-input-editable" required placeholder="+1-555-019-4821" />
                <span style="font-size: 0.71rem; color: var(--text-dim); margin-top: 0.15rem;">Tip: Change to your personal mobile number to test receiving the real call.</span>
              </div>
            </div>

            <div class="form-group">
              <label class="form-label">Item Description & Quantity <span class="badge-readonly">Auto-Populated</span></label>
              <input type="text" id="form-item-desc" class="form-input form-input-readonly" readonly required placeholder="5,000 units Optical Transceivers" />
            </div>

            <div class="form-group">
              <label class="form-label">Telephony Execution Mode</label>
              <select id="form-mode" class="form-select" onchange="handleModeChange()">
                <option value="live" selected>Live CALL-E Telephony Network (Outbound Line)</option>
                <option value="mock">High-Fidelity Offline Simulator (Instant / Zero API Cost)</option>
              </select>
            </div>

            <div class="modal-actions-row" style="display: flex; justify-content: flex-end; gap: 0.75rem; margin-top: 0.5rem;">
              <button type="button" class="btn btn-secondary" onclick="closeNewCallModal()">Cancel</button>
              <button type="submit" class="btn btn-primary" id="btn-submit-call">
                <span>🚀</span> Dispatch Call via CALL-E
              </button>
            </div>
          </form>
        </div>

        <!-- VIEW 2: In-Modal Call Execution & Outcome Panel -->
        <div id="call-execution-panel" style="display: none; flex-direction: column; gap: 1rem;">
          <!-- Execution Target Summary Bar -->
          <div class="execution-summary-bar">
            <div>
              <div style="font-size: 0.7rem; color: var(--text-muted); text-transform: uppercase;">Call Destination</div>
              <div style="font-weight: 700; font-size: 0.88rem; color: var(--text-main); display: flex; align-items: center; gap: 0.4rem; margin-top: 2px;">
                <span id="progress-dial-number">+1-555-019-4821</span>
                <span style="color: var(--text-dim); font-weight: normal;">(<span id="progress-contact-name">Contact</span> - <span id="progress-order-id">PO</span>)</span>
              </div>
            </div>
            <div style="display: flex; align-items: center; gap: 0.6rem;">
              <span id="progress-mode-badge" style="font-size: 0.72rem; padding: 3px 8px; border-radius: 4px; font-weight: 600; background: rgba(59, 130, 246, 0.15); color: var(--accent-blue);">Live Line</span>
              <span id="call-progress-timer" style="font-family: monospace; font-size: 0.88rem; color: var(--accent-cyan); font-weight: 700;">00:00</span>
            </div>
          </div>

          <!-- Live Call Execution Progress Stepper -->
          <div id="call-progress-card" style="display: flex; background: var(--bg-secondary); border: 1px solid var(--accent-blue); border-radius: var(--radius-md); padding: 1rem 1.15rem; flex-direction: column; gap: 0.7rem;">
            <div style="display: flex; align-items: center; justify-content: space-between; border-bottom: 1px solid var(--card-border); padding-bottom: 0.5rem;">
              <div style="font-weight: 700; font-size: 0.86rem; display: flex; align-items: center; gap: 0.45rem;">
                <span class="pulse-dot" id="progress-pulse-dot" style="background-color: var(--accent-blue);"></span>
                <span id="call-progress-title">Telephony Execution in Progress...</span>
              </div>
            </div>

            <div style="display: flex; flex-direction: column; gap: 0.5rem; font-size: 0.8rem;">
              <div id="pstep-1" style="display: flex; align-items: center; gap: 0.45rem; color: var(--text-muted);">
                <span id="picon-1" style="font-size: 0.95rem;">⏳</span>
                <span id="plbl-1">1. Transmitting parameters to Python FastAPI backend...</span>
              </div>
              <div id="pstep-2" style="display: flex; align-items: center; gap: 0.45rem; color: var(--text-muted);">
                <span id="picon-2" style="font-size: 0.95rem;">⏳</span>
                <span id="plbl-2">2. Initializing CALL-E telephony client & carrier line...</span>
              </div>
              <div id="pstep-3" style="display: flex; align-items: center; gap: 0.45rem; color: var(--text-muted);">
                <span id="picon-3" style="font-size: 0.95rem;">⏳</span>
                <span id="plbl-3">3. Telephony network dialing destination phone & AI agent conversing...</span>
              </div>
              <div id="pstep-4" style="display: flex; align-items: center; gap: 0.45rem; color: var(--text-muted);">
                <span id="picon-4" style="font-size: 0.95rem;">⏳</span>
                <span id="plbl-4">4. Extracting structured fulfillment details & persisting to SQLite DB...</span>
              </div>
            </div>
          </div>

          <!-- Error Feedback Container (shown when live call halts or server error) -->
          <div id="call-error-box" class="call-error-box" style="display: none;">
            <div style="display: flex; align-items: flex-start; gap: 0.75rem;">
              <span style="font-size: 1.3rem;">❌</span>
              <div style="flex: 1;">
                <div style="font-weight: 700; font-size: 0.9rem; color: #f87171;" id="call-error-title">Telephony Dispatch Halted</div>
                <div style="font-size: 0.82rem; color: var(--text-muted); margin-top: 0.35rem; line-height: 1.45;" id="call-error-message"></div>
                <div style="font-size: 0.76rem; color: var(--text-dim); margin-top: 0.5rem; background: rgba(0,0,0,0.2); padding: 0.5rem 0.75rem; border-radius: var(--radius-sm);" id="call-error-guide">
                  <strong>Why did this happen?</strong> Live calls to mobile numbers require a valid <code>CALLE_API_KEY</code> configured in <code>/var/www/call-e-hackathon/.env</code> on the server. You can test the complete verification flow immediately using the <strong>Offline Simulator</strong>.
                </div>
              </div>
            </div>
            <div style="display: flex; justify-content: flex-end; gap: 0.6rem; margin-top: 0.5rem; flex-wrap: wrap;">
              <button type="button" class="btn btn-secondary" onclick="returnToFormView()">← Back to Edit Form</button>
              <button type="button" class="btn btn-primary" onclick="switchToSimulatorAndRun()">⚡ Run in Offline Simulator</button>
              <button type="button" class="btn btn-secondary" onclick="closeNewCallModal()">Close</button>
            </div>
          </div>

          <!-- Success & Dialogue Outcome Container (shown when call finishes) -->
          <div id="call-success-box" class="call-outcome-box" style="display: none;">
            <div style="display: flex; align-items: center; justify-content: space-between; border-bottom: 1px solid var(--card-border); padding-bottom: 0.6rem;">
              <div style="font-weight: 700; font-size: 0.9rem; color: var(--accent-green); display: flex; align-items: center; gap: 0.4rem;">
                <span>✅</span> <span id="call-success-title">Verification Call Completed</span>
              </div>
              <span id="call-success-status-pill" class="badge"></span>
            </div>

            <!-- Structured Findings Grid -->
            <div class="outcome-findings-grid" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(120px, 1fr)); gap: 0.6rem; font-size: 0.78rem;">
              <div style="background: var(--bg-primary); padding: 0.5rem 0.7rem; border-radius: var(--radius-sm);">
                <div style="color: var(--text-muted); font-size: 0.68rem; text-transform: uppercase;">Revised Date</div>
                <div id="outcome-revised-date" style="font-weight: 700; margin-top: 2px;"></div>
              </div>
              <div style="background: var(--bg-primary); padding: 0.5rem 0.7rem; border-radius: var(--radius-sm);">
                <div style="color: var(--text-muted); font-size: 0.68rem; text-transform: uppercase;">Delay Impact</div>
                <div id="outcome-delay-days" style="font-weight: 700; margin-top: 2px;"></div>
              </div>
              <div style="background: var(--bg-primary); padding: 0.5rem 0.7rem; border-radius: var(--radius-sm);">
                <div style="color: var(--text-muted); font-size: 0.68rem; text-transform: uppercase;">Root Cause</div>
                <div id="outcome-category" style="font-weight: 700; margin-top: 2px;"></div>
              </div>
              <div style="background: var(--bg-primary); padding: 0.5rem 0.7rem; border-radius: var(--radius-sm);">
                <div style="color: var(--text-muted); font-size: 0.68rem; text-transform: uppercase;">Financial Exposure</div>
                <div id="outcome-impact" style="font-weight: 700; color: #f87171; margin-top: 2px;"></div>
              </div>
            </div>

            <!-- Conversational Transcript (shown directly in the same modal) -->
            <div>
              <div style="font-size: 0.76rem; font-weight: 700; color: var(--text-muted); margin-bottom: 0.4rem; text-transform: uppercase; letter-spacing: 0.04em; display: flex; align-items: center; justify-content: space-between;">
                <span>💬 Conversational Dialogue Transcript</span>
                <span id="outcome-transcript-badge" style="font-size: 0.68rem; font-weight: normal; color: var(--text-dim);"></span>
              </div>
              <div class="transcript-box" id="call-result-transcript" style="max-height: 220px; overflow-y: auto;">
                <!-- Chat bubbles rendered here -->
              </div>
            </div>

            <div style="display: flex; justify-content: flex-end; gap: 0.6rem; margin-top: 0.5rem; flex-wrap: wrap;">
              <button type="button" class="btn btn-secondary" onclick="returnToFormView(true)">📞 Trigger Another Call</button>
              <button type="button" class="btn btn-primary" onclick="closeNewCallModal()">✓ Close & View in Dashboard</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>

  <!-- Footer -->
  <footer class="app-footer">
    <div>
      <strong>CALL-E Autonomous Voice Operations</strong> | Supply Chain Telephony Control Tower
    </div>
    <div>
      Powered by CALL-E Server SDK &bull; High-Fidelity Simulation Engine &bull; Pydantic Core
    </div>
  </footer>

  <!-- Raw Embedded Report Data for Zero-Dependency Offline Rendering -->
  <script id="report-data" type="application/json">
{report_json_str}
  </script>

  <!-- Application Logic & Reactivity -->
  <script>
    // Server Configuration & State management
    let reportState = JSON.parse(document.getElementById('report-data').textContent);
    let allCalls = reportState.call_records || [];
    let currentStatusFilter = 'ALL';
    let currentViewMode = 'table';
    let activeModalCall = null;

    // Populate Category dropdown
    function populateCategories() {{
      const select = document.getElementById('category-filter');
      const categories = new Set();
      allCalls.forEach(c => {{
        if (c.delay_category && c.delay_category !== 'NONE') {{
          categories.add(c.delay_category);
        }}
      }});
      select.innerHTML = '<option value="ALL">All Root Causes</option>';
      categories.forEach(cat => {{
        const opt = document.createElement('option');
        opt.value = cat;
        opt.textContent = cat.replace(/_/g, ' ');
        select.appendChild(opt);
      }});
    }}

    // Populate Supplier Selection & Pre-fill Trigger Modal
    function populateSupplierSelect(selectedOrderId = null) {{
      const select = document.getElementById('form-supplier-select');
      select.innerHTML = '';
      const seen = new Set();
      let targetCall = null;

      if (selectedOrderId) {{
        targetCall = allCalls.find(c => c.order_id === selectedOrderId);
      }}
      if (!targetCall && allCalls.length > 0) {{
        targetCall = allCalls[0];
      }}

      allCalls.forEach(c => {{
        if (!seen.has(c.supplier_name)) {{
          seen.add(c.supplier_name);
          const opt = document.createElement('option');
          opt.value = c.supplier_name;
          opt.textContent = `${{c.supplier_name}} (${{c.order_id}} - ${{c.contact_name}})`;
          opt.dataset.orderId = c.order_id;
          opt.dataset.contact = c.contact_name;
          opt.dataset.phone = c.phone_number;
          opt.dataset.deliveryDate = c.revised_delivery_date || c.original_delivery_date || '';
          opt.dataset.itemDesc = c.delay_notes || 'Confirmed procurement verification units';

          if (targetCall && targetCall.supplier_name === c.supplier_name) {{
            opt.selected = true;
          }}
          select.appendChild(opt);
        }}
      }});

      const customOpt = document.createElement('option');
      customOpt.value = '__CUSTOM__';
      customOpt.textContent = '➕ Custom Supplier (Manual Entry)';
      select.appendChild(customOpt);

      if (targetCall) {{
        fillFormFieldsFromCall(targetCall);
      }}
    }}

    function fillFormFieldsFromCall(c) {{
      if (!c) return;
      document.getElementById('form-po-id').value = c.order_id || 'PO-99500';
      document.getElementById('form-delivery-date').value = c.revised_delivery_date || c.original_delivery_date || new Date().toISOString().slice(0, 10);
      document.getElementById('form-contact-name').value = c.contact_name || '';
      document.getElementById('form-phone').value = c.phone_number || '';
      document.getElementById('form-item-desc').value = c.delay_notes || 'Standard procurement batch';
    }}

    function populateSupplierFields() {{
      const select = document.getElementById('form-supplier-select');
      const selected = select.options[select.selectedIndex];
      if (!selected) return;

      const isCustom = (selected.value === '__CUSTOM__');
      ['form-po-id', 'form-delivery-date', 'form-contact-name', 'form-item-desc'].forEach(id => {{
        const el = document.getElementById(id);
        if (el) {{
          el.readOnly = !isCustom;
          if (isCustom) {{
            el.classList.remove('form-input-readonly');
          }} else {{
            el.classList.add('form-input-readonly');
          }}
        }}
      }});

      if (isCustom) {{
        document.getElementById('form-po-id').value = 'PO-' + Math.floor(10000 + Math.random() * 90000);
        document.getElementById('form-delivery-date').value = new Date().toISOString().slice(0, 10);
        document.getElementById('form-contact-name').value = '';
        document.getElementById('form-phone').value = '';
        document.getElementById('form-item-desc').value = 'Procurement fulfillment verification';
        return;
      }}

      if (selected.dataset.orderId) {{
        document.getElementById('form-po-id').value = selected.dataset.orderId;
        document.getElementById('form-delivery-date').value = selected.dataset.deliveryDate;
        document.getElementById('form-contact-name').value = selected.dataset.contact;
        document.getElementById('form-phone').value = selected.dataset.phone;
        document.getElementById('form-item-desc').value = selected.dataset.itemDesc;
      }}
    }}


    // Update Analytics Charts & Distribution
    function updateAnalytics() {{
      const total = allCalls.length;
      if (total === 0) return;

      const onTime = allCalls.filter(c => c.fulfillment_status === 'ON_TIME').length;
      const delayed = allCalls.filter(c => c.fulfillment_status === 'DELAYED').length;
      const partial = allCalls.filter(c => c.fulfillment_status === 'PARTIAL_DISPATCH').length;
      const unreachable = allCalls.filter(c => c.fulfillment_status === 'UNREACHABLE').length;
      const escalations = allCalls.filter(c => c.escalation_required).length;

      // Status distribution bars strictly matching top KPI color semantics:
      // On-Time = Green, Delayed = Yellow, Partial = Info Cyan, Unreachable = Gray, Escalation = Red
      const statusContainer = document.getElementById('status-distribution-bars');
      statusContainer.innerHTML = `
        ${{renderBarItem('On-Time Fulfillment', onTime, total, 'var(--accent-green)')}}
        ${{renderBarItem('Delayed Shipments', delayed, total, 'var(--accent-amber)')}}
        ${{renderBarItem('Partial Dispatches', partial, total, '#38bdf8')}}
        ${{renderBarItem('Unreachable / Voicemail', unreachable, total, '#64748b')}}
        ${{renderBarItem('Critical Escalations', escalations, total, 'var(--accent-red)')}}
      `;

      // Consolidated Delay Root Cause Taxonomy & Financial Exposure (count + risk side-by-side)
      const categoryData = {{}};
      let maxCategoryRisk = 0;
      allCalls.forEach(c => {{
        if (c.delay_category && c.delay_category !== 'NONE') {{
          const cat = c.delay_category.replace(/_/g, ' ');
          if (!categoryData[cat]) {{
            categoryData[cat] = {{ count: 0, risk: 0 }};
          }}
          categoryData[cat].count += 1;
          categoryData[cat].risk += (c.estimated_financial_impact_usd || 0);
          if (categoryData[cat].risk > maxCategoryRisk) {{
            maxCategoryRisk = categoryData[cat].risk;
          }}
        }}
      }});

      const catContainer = document.getElementById('delay-category-bars');
      const entries = Object.entries(categoryData);
      if (entries.length === 0) {{
        catContainer.innerHTML = '<div style="color:var(--text-muted);font-size:0.8rem;padding:0.5rem 0;">No delay disruptions recorded</div>';
      }} else {{
        entries.sort((a, b) => b[1].risk - a[1].risk || b[1].count - a[1].count);
        catContainer.innerHTML = entries.map(([cat, data]) => {{
          const countPct = Math.round((data.count / (delayed || 1)) * 100);
          return renderConsolidatedBarItem(cat, data.count, countPct, data.risk, maxCategoryRisk);
        }}).join('');
      }}

      // Backwards-compatible risk-category-bars
      const riskContainer = document.getElementById('risk-category-bars');
      if (riskContainer) {{
        riskContainer.innerHTML = '';
      }}

      // Update Filter Pill counts
      document.getElementById('pill-count-all').textContent = total;
      document.getElementById('pill-count-ontime').textContent = onTime;
      document.getElementById('pill-count-delayed').textContent = delayed;
      document.getElementById('pill-count-partial').textContent = partial;
      document.getElementById('pill-count-unreachable').textContent = unreachable;
      document.getElementById('pill-count-escalations').textContent = escalations;
    }}

    function renderConsolidatedBarItem(label, count, countPct, riskUsd, maxRisk) {{
      const riskPct = maxRisk > 0 ? Math.round((riskUsd / maxRisk) * 100) : countPct;
      const riskStr = riskUsd > 0 ? `$${{riskUsd.toLocaleString()}}` : '$0';
      const barColor = riskUsd >= 10000 ? 'var(--accent-red)' : (riskUsd > 0 ? 'var(--accent-amber)' : 'var(--accent-green)');
      return `
        <div class="bar-item">
          <div class="bar-label-row">
            <span style="font-weight:600; color:var(--text-main); font-size:0.82rem;">${{label}}</span>
            <div style="display:flex; align-items:center; gap:0.75rem;">
              <span style="color:var(--text-muted); font-size:0.78rem;">${{count}} orders (${{countPct}}%)</span>
              <strong style="color:${{riskUsd > 0 ? 'var(--accent-red)' : 'var(--text-muted)'}}; font-size:0.84rem;">${{riskStr}}</strong>
            </div>
          </div>
          <div class="bar-track">
            <div class="bar-fill" style="width: ${{Math.max(riskPct, 6)}}%; background-color: ${{barColor}};"></div>
          </div>
        </div>
      `;
    }}

    function renderBarItem(label, val, total, color) {{
      const pct = Math.round((val / total) * 100) || 0;
      return `
        <div class="bar-item">
          <div class="bar-label-row">
            <span>${{label}}</span>
            <strong>${{val}} (${{pct}}%)</strong>
          </div>
          <div class="bar-track">
            <div class="bar-fill" style="width: ${{pct}}%; background-color: ${{color}};"></div>
          </div>
        </div>
      `;
    }}

    // Filter and Sort Engine
    function applyFilters() {{
      const rawQuery = (document.getElementById('search-input').value || '').trim();
      const query = rawQuery.toLowerCase();
      const queryDigits = rawQuery.replace(/\\D/g, '');
      const catFilter = document.getElementById('category-filter').value;
      const sortMode = document.getElementById('sort-filter').value;

      let filtered = allCalls.filter(c => {{
        // Status filter
        if (currentStatusFilter === 'ON_TIME' && c.fulfillment_status !== 'ON_TIME') return false;
        if (currentStatusFilter === 'DELAYED' && c.fulfillment_status !== 'DELAYED') return false;
        if (currentStatusFilter === 'PARTIAL_DISPATCH' && c.fulfillment_status !== 'PARTIAL_DISPATCH') return false;
        if (currentStatusFilter === 'UNREACHABLE' && c.fulfillment_status !== 'UNREACHABLE') return false;
        if (currentStatusFilter === 'ESCALATION' && !c.escalation_required) return false;

        // Category filter
        if (catFilter !== 'ALL' && c.delay_category !== catFilter) return false;

        // Text query
        if (query) {{
          const matchTarget = `${{c.order_id}} ${{c.supplier_name}} ${{c.contact_name}} ${{c.phone_number || ''}} ${{c.call_id || ''}} ${{c.escalation_contact_name || ''}} ${{c.escalation_contact_phone || ''}} ${{c.delay_notes || ''}} ${{c.delay_category || ''}}`.toLowerCase();
          let matched = matchTarget.includes(query);
          if (!matched && queryDigits.length >= 3) {{
            const phoneDigits = (c.phone_number || '').replace(/\\D/g, '');
            const escDigits = (c.escalation_contact_phone || '').replace(/\\D/g, '');
            if (phoneDigits.includes(queryDigits) || escDigits.includes(queryDigits)) {{
              matched = true;
            }}
          }}
          if (!matched) return false;
        }}

        return true;
      }});

      // Sort
      if (sortMode === 'RISK_DESC') {{
        filtered.sort((a, b) => b.estimated_financial_impact_usd - a.estimated_financial_impact_usd);
      }} else if (sortMode === 'DELAY_DESC') {{
        filtered.sort((a, b) => b.delay_days - a.delay_days);
      }} else if (sortMode === 'DATE_ASC') {{
        filtered.sort((a, b) => (a.original_delivery_date || '').localeCompare(b.original_delivery_date || ''));
      }} else if (sortMode === 'SUPPLIER_ASC') {{
        filtered.sort((a, b) => a.supplier_name.localeCompare(b.supplier_name));
      }}

      renderTableView(filtered);
      renderCardsView(filtered);
    }}

    // Render Table View
    function renderTableView(records) {{
      const tbody = document.getElementById('calls-table-body');
      if (records.length === 0) {{
        tbody.innerHTML = `<tr><td colspan="11" style="text-align:center;padding:2rem;color:var(--text-muted);">No matching call records found</td></tr>`;
        return;
      }}

      tbody.innerHTML = records.map(r => {{
        const statusClass = getStatusClass(r.fulfillment_status);
        const statusIcon = getStatusIcon(r.fulfillment_status);
        const delayStr = r.delay_days > 0 ? `+${{r.delay_days}}d` : '0d';
        const riskStr = r.estimated_financial_impact_usd > 0 ? `$${{r.estimated_financial_impact_usd.toLocaleString()}}` : '$0';

        // Simplify Ledger Columns: Clean supplier name without noise
        const supplierDisplay = `<div style="font-weight:600; color:var(--text-main); font-size:0.84rem;">${{r.supplier_name}}</div>`;

        // Simplify Ledger Columns: Clean escalation lead name without phone number or lengthy parenthetical titles
        const rawLead = r.escalation_contact_name || r.contact_name || '-';
        const cleanLead = rawLead.replace(/\\s*\\(.*?\\)\\s*/g, '').trim();

        // Clean Truncation: Standard CSS ellipsis + native browser hover tooltip
        const rawItemDesc = r.item_description || r.delay_notes || 'Standard Delivery Batch';
        const safeTooltip = rawItemDesc.replace(/"/g, '&quot;');

        return `
          <tr onclick="openCallModal('${{r.call_id}}')">
            <td>
              <span class="status-badge ${{statusClass}}">${{statusIcon}} ${{r.fulfillment_status}}</span>
            </td>
            <td>
              <strong>${{r.order_id}}</strong>
            </td>
            <td>
              ${{supplierDisplay}}
            </td>
            <td>
              <div style="max-width:220px; overflow:hidden; text-overflow:ellipsis; white-space:nowrap;" title="${{safeTooltip}}">
                ${{rawItemDesc}}
              </div>
            </td>
            <td>${{r.original_delivery_date || '-'}}</td>
            <td><strong>${{r.revised_delivery_date || r.original_delivery_date || '-'}}</strong></td>
            <td><strong style="color:${{r.delay_days > 0 ? 'var(--accent-amber)' : 'inherit'}};">${{delayStr}}</strong></td>
            <td><span style="font-size:0.75rem;color:var(--text-muted);">${{r.delay_category !== 'NONE' ? r.delay_category.replace(/_/g, ' ') : '-'}}</span></td>
            <td><strong style="color:${{r.estimated_financial_impact_usd > 0 ? 'var(--accent-red)' : 'var(--text-muted)'}};">${{riskStr}}</strong></td>
            <td>
              <span style="font-size:0.82rem; font-weight:500; color:var(--text-main);">${{cleanLead}}</span>
            </td>
            <td>
              <div style="display: flex; gap: 0.4rem; align-items: center;">
                <button class="btn-action-view" onclick="event.stopPropagation(); openCallModal('${{r.call_id}}')" title="Inspect call transcript for ${{r.order_id}}">
                  👁️ View Call
                </button>
                <button class="btn btn-primary" style="padding: 0.32rem 0.65rem; font-size: 0.72rem; font-weight:600;" onclick="event.stopPropagation(); openNewCallModal('${{r.order_id}}')" title="Place verification call for ${{r.order_id}}">
                  📞 Call
                </button>
              </div>
            </td>
          </tr>
        `;
      }}).join('');
    }}

    // Render Cards View
    function renderCardsView(records) {{
      const container = document.getElementById('cards-view-section');
      if (records.length === 0) {{
        container.innerHTML = `<div style="grid-column:1/-1;text-align:center;padding:2rem;color:var(--text-muted);">No matching call records found</div>`;
        return;
      }}

      container.innerHTML = records.map(r => {{
        const statusClass = getStatusClass(r.fulfillment_status);
        const statusIcon = getStatusIcon(r.fulfillment_status);
        const escTag = r.escalation_required ? `<span class="escalation-tag">🚨 ESCALATE</span>` : '';

        return `
          <div class="call-card" onclick="openCallModal('${{r.call_id}}')">
            <div class="call-card-top">
              <div>
                <div class="card-po">
                  ${{r.order_id}}
                </div>
                <div class="card-supplier">${{r.supplier_name}}</div>
              </div>
              <div style="text-align:right;">
                <span class="status-badge ${{statusClass}}">${{statusIcon}} ${{r.fulfillment_status}}</span>
                <div style="margin-top:0.25rem;">${{escTag}}</div>
              </div>
            </div>

            <div class="card-item">${{r.delay_notes || 'All quantities confirmed on schedule for target date.'}}</div>

            <div class="card-metrics-row">
              <div>
                <div class="card-metric-val">${{r.original_delivery_date}}</div>
                <div class="card-metric-lbl">Target Date</div>
              </div>
              <div>
                <div class="card-metric-val" style="color:${{r.delay_days > 0 ? 'var(--accent-amber)' : 'inherit'}};">+${{r.delay_days}}d</div>
                <div class="card-metric-lbl">Delay Days</div>
              </div>
              <div>
                <div class="card-metric-val" style="color:${{r.estimated_financial_impact_usd > 0 ? 'var(--accent-red)' : 'inherit'}};">$${{r.estimated_financial_impact_usd.toLocaleString()}}</div>
                <div class="card-metric-lbl">Risk Impact</div>
              </div>
            </div>

            <div class="card-footer">
              <div style="display: flex; flex-direction: column; gap: 0.15rem; min-width: 0;">
                <span style="overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">👤 ${{r.escalation_contact_name || r.contact_name}}</span>
                <span style="font-family:monospace; font-size: 0.78rem;">${{r.escalation_contact_phone || r.phone_number}}</span>
              </div>
              <div class="card-footer-actions" style="display: flex; gap: 0.4rem; align-items: center;">
                <button class="btn-action-view" onclick="event.stopPropagation(); openCallModal('${{r.call_id}}')" title="Inspect call transcript for ${{r.order_id}}">
                  👁️ View Call
                </button>
                <button class="btn btn-primary" style="padding: 0.32rem 0.65rem; font-size: 0.72rem; font-weight:600;" onclick="event.stopPropagation(); openNewCallModal('${{r.order_id}}')" title="Place verification call for ${{r.order_id}}">
                  📞 Call
                </button>
              </div>
            </div>
          </div>
        `;
      }}).join('');
    }}

    function getStatusClass(status) {{
      if (status === 'ON_TIME') return 'on-time';
      if (status === 'DELAYED') return 'delayed';
      if (status === 'PARTIAL_DISPATCH') return 'partial';
      if (status === 'UNREACHABLE') return 'unreachable';
      return '';
    }}

    function getStatusIcon(status) {{
      if (status === 'ON_TIME') return '✅';
      if (status === 'DELAYED') return '⚠️';
      if (status === 'PARTIAL_DISPATCH') return '📦';
      if (status === 'UNREACHABLE') return '📵';
      return '❓';
    }}

    function setStatusFilter(status) {{
      currentStatusFilter = status;
      document.querySelectorAll('#status-filter-pills .filter-pill').forEach(btn => {{
        btn.classList.remove('active');
      }});
      event.currentTarget.classList.add('active');
      applyFilters();
    }}

    function setViewMode(mode) {{
      currentViewMode = mode;
      const tableSec = document.getElementById('table-view-section');
      const cardsSec = document.getElementById('cards-view-section');
      const btnTable = document.getElementById('btn-view-table');
      const btnCards = document.getElementById('btn-view-cards');

      if (mode === 'table') {{
        tableSec.style.display = 'block';
        cardsSec.style.display = 'none';
        btnTable.classList.add('active');
        btnCards.classList.remove('active');
      }} else {{
        tableSec.style.display = 'none';
        cardsSec.style.display = 'grid';
        btnCards.classList.add('active');
        btnTable.classList.remove('active');
      }}
    }}

    // Call Details Modal
    function openCallModal(callId) {{
      const call = allCalls.find(c => c.call_id === callId);
      if (!call) return;

      activeModalCall = call;
      document.getElementById('modal-po-header').textContent = `${{call.order_id}} • ${{call.supplier_name}}`;
      document.getElementById('modal-call-id').textContent = call.call_id;
      document.getElementById('modal-contact-name').textContent = call.contact_name;
      document.getElementById('modal-phone').textContent = call.phone_number;
      document.getElementById('modal-duration').textContent = `${{call.call_duration_seconds || 84}} seconds`;

      // Financial details
      const formula = call.fulfillment_status === 'ON_TIME'
        ? 'Zero penalty assessed (Fulfillment on target schedule)'
        : `(${{call.delay_days}} days &times; $1,500/day penalty) + $${{call.expedited_freight_cost_usd.toLocaleString()}} freight surcharge`;
      document.getElementById('modal-risk-formula').innerHTML = formula;
      document.getElementById('modal-total-impact').textContent = `$${{call.estimated_financial_impact_usd.toLocaleString()}} Exposure`;

      // Escalation contact
      document.getElementById('modal-esc-name').textContent = call.escalation_contact_name || call.contact_name;
      document.getElementById('modal-esc-phone').textContent = call.escalation_contact_phone || call.phone_number;

      // Render Transcript bubbles
      renderTranscript(call.raw_transcript, call.contact_name);

      document.getElementById('call-modal').classList.add('active');
    }}

    function closeCallModal() {{
      document.getElementById('call-modal').classList.remove('active');
    }}

    function handleModalBackdropClick(e) {{
      if (e.target.id === 'call-modal') closeCallModal();
    }}

    // Transcript Renderer with Highlight Chips
    function renderTranscript(rawText, supplierContact) {{
      const container = document.getElementById('modal-transcript-container');
      container.innerHTML = '';

      if (!rawText) {{
        container.innerHTML = '<div style="color:var(--text-muted);text-align:center;padding:1rem;">Conversational transcript being processed...</div>';
        return;
      }}

      const lines = rawText.split('\\n');
      lines.forEach(line => {{
        line = line.trim();
        if (!line) return;

        let speaker = 'Agent';
        let body = line;
        if (line.startsWith('Agent:')) {{
          speaker = 'Agent';
          body = line.substring(6).trim();
        }} else if (line.startsWith('Supplier:')) {{
          speaker = 'Supplier';
          body = line.substring(9).trim();
        }} else if (line.startsWith('Automated System:')) {{
          speaker = 'Automated System';
          body = line.substring(17).trim();
        }}

        // Format highlight tags in body
        body = body
          .replace(/(PO-[0-9]+)/g, '<span class="entity-tag">$1</span>')
          .replace(/(\\$\\s?[0-9,]+(?:\\.[0-9]{{2}})?)/g, '<span class="entity-tag">$1</span>')
          .replace(/(\\b\\d{{4}}-\\d{{2}}-\\d{{2}}\\b)/g, '<span class="entity-tag">$1</span>');

        const bubble = document.createElement('div');
        bubble.className = `chat-bubble ${{speaker === 'Agent' ? 'agent' : 'supplier'}}`;
        bubble.innerHTML = `
          <div class="speaker-name ${{speaker === 'Agent' ? 'agent-lbl' : 'supplier-lbl'}}">
            ${{speaker === 'Agent' ? '🤖 Alex (CALL-E Autonomous Agent)' : (speaker === 'Supplier' ? `👤 ${{supplierContact || 'Dispatcher'}}` : '📞 Voicemail System')}}
          </div>
          <div>${{body}}</div>
        `;
        container.appendChild(bubble);
      }});
    }}

    // Telephony Readiness Notice Updater
    function updateServerTelephonyBanner() {{
      const banner = document.getElementById('server-telephony-banner');
      if (!banner) return;
      const modeSelect = document.getElementById('form-mode');
      const mode = modeSelect ? modeSelect.value : 'live';

      if (mode === 'mock') {{
        banner.style.display = 'block';
        banner.className = 'telephony-banner ready';
        banner.innerHTML = '<span class="pulse-dot" style="background:#10b981; display:inline-block;"></span> <strong>Offline Simulator Active:</strong> Instant deterministic simulation with zero telephony API cost.';
        return;
      }}

      if (window.serverHasApiKey) {{
        banner.style.display = 'block';
        banner.className = 'telephony-banner ready';
        banner.innerHTML = '<span class="pulse-dot" style="background:#10b981; display:inline-block;"></span> <strong>Carrier Line Active:</strong> Server CALLE_API_KEY loaded in environment. Outbound voice calls ready to dispatch.';
      }} else {{
        banner.style.display = 'block';
        banner.className = 'telephony-banner warning';
        banner.innerHTML = '<strong>⚠️ Server Telephony Notice:</strong> Server has no <code>CALLE_API_KEY</code> configured in <code>.env</code>. Live calls to real mobile numbers will halt until an API key is configured. Switch mode below to <strong>Offline Simulator</strong> to test the full flow without live API credits.';
      }}
    }}

    function handleModeChange() {{
      updateServerTelephonyBanner();
    }}

    // Trigger New Call Modal Controls
    function openNewCallModal(orderId = null) {{
      returnToFormView(orderId === null);
      populateSupplierSelect(orderId);
      updateServerTelephonyBanner();
      document.getElementById('new-call-modal').classList.add('active');
    }}

    function closeNewCallModal() {{
      document.getElementById('new-call-modal').classList.remove('active');
    }}

    function handleNewCallBackdropClick(e) {{
      if (e.target.id === 'new-call-modal') closeNewCallModal();
    }}

    function returnToFormView(reset = false) {{
      const formView = document.getElementById('new-call-form-view');
      const execPanel = document.getElementById('call-execution-panel');
      const errorBox = document.getElementById('call-error-box');
      const successBox = document.getElementById('call-success-box');
      const modalTitle = document.getElementById('new-call-modal-title');
      const btn = document.getElementById('btn-submit-call');

      if (formView) formView.style.display = 'block';
      if (execPanel) execPanel.style.display = 'none';
      if (errorBox) errorBox.style.display = 'none';
      if (successBox) successBox.style.display = 'none';
      if (modalTitle) modalTitle.innerHTML = '<span>📞</span> Trigger Autonomous Outbound Call';
      if (btn) {{
        btn.disabled = false;
        btn.innerHTML = '<span>🚀</span> Dispatch Call via CALL-E';
      }}

      if (reset) {{
        populateSupplierSelect();
      }}
      updateServerTelephonyBanner();
    }}

    function switchToSimulatorAndRun() {{
      const modeSelect = document.getElementById('form-mode');
      if (modeSelect) modeSelect.value = 'mock';
      updateServerTelephonyBanner();
      executeManualCall();
    }}

    async function executeManualCall(e) {{
      if (e && e.preventDefault) e.preventDefault();
      const btn = document.getElementById('btn-submit-call');
      if (btn) btn.disabled = true;

      const poId = document.getElementById('form-po-id').value.trim();
      const deliveryDate = document.getElementById('form-delivery-date').value;
      const contactName = document.getElementById('form-contact-name').value.trim();
      const phone = document.getElementById('form-phone').value.trim();
      const itemDesc = document.getElementById('form-item-desc').value.trim();
      const mode = document.getElementById('form-mode').value;
      const select = document.getElementById('form-supplier-select');
      const supplierName = (select.value === '__CUSTOM__' || !select.value) ? 'Custom Supplier Logistics' : select.value;

      // Validate phone number
      const phoneDigits = phone.replace(/\\D/g, '');
      if (mode === 'live' && phoneDigits.length < 10) {{
        alert('Please enter a valid phone number with area code (at least 10 digits) to dispatch an outbound call.');
        if (btn) btn.disabled = false;
        return;
      }}

      // Transition to In-Modal Call Execution & Monitoring Panel
      const formView = document.getElementById('new-call-form-view');
      const execPanel = document.getElementById('call-execution-panel');
      const progressCard = document.getElementById('call-progress-card');
      const errorBox = document.getElementById('call-error-box');
      const successBox = document.getElementById('call-success-box');
      const timerElem = document.getElementById('call-progress-timer');
      const progressTitle = document.getElementById('call-progress-title');
      const modalTitle = document.getElementById('new-call-modal-title');

      if (formView) formView.style.display = 'none';
      if (execPanel) execPanel.style.display = 'flex';
      if (progressCard) progressCard.style.display = 'flex';
      if (errorBox) errorBox.style.display = 'none';
      if (successBox) successBox.style.display = 'none';

      if (modalTitle) modalTitle.innerHTML = '<span>📞</span> Outbound Verification Call Monitor';
      if (progressTitle) progressTitle.textContent = mode === 'live' ? 'Telephony Execution in Progress...' : 'Offline Simulation in Progress...';

      // Update Summary Bar
      const dialNumberElem = document.getElementById('progress-dial-number');
      const contactElem = document.getElementById('progress-contact-name');
      const orderElem = document.getElementById('progress-order-id');
      const modeBadge = document.getElementById('progress-mode-badge');

      if (dialNumberElem) dialNumberElem.textContent = phone;
      if (contactElem) contactElem.textContent = contactName;
      if (orderElem) orderElem.textContent = poId;
      if (modeBadge) {{
        modeBadge.textContent = mode === 'live' ? 'Live Telephony Line' : 'Offline Simulator';
        modeBadge.style.color = mode === 'live' ? 'var(--accent-blue)' : 'var(--accent-green)';
        modeBadge.style.background = mode === 'live' ? 'rgba(59, 130, 246, 0.15)' : 'rgba(16, 185, 129, 0.15)';
      }}

      function setStep(num, state, msg = null) {{
        const icon = document.getElementById(`picon-${{num}}`);
        const lbl = document.getElementById(`plbl-${{num}}`);
        const step = document.getElementById(`pstep-${{num}}`);
        if (!icon || !lbl || !step) return;
        if (msg) lbl.innerHTML = msg;
        if (state === 'active') {{
          icon.textContent = '🔄';
          step.style.color = 'var(--accent-blue)';
          step.style.fontWeight = '600';
        }} else if (state === 'done') {{
          icon.textContent = '✅';
          step.style.color = 'var(--accent-green)';
          step.style.fontWeight = '500';
        }} else if (state === 'error') {{
          icon.textContent = '❌';
          step.style.color = 'var(--accent-red)';
          step.style.fontWeight = '600';
        }} else {{
          icon.textContent = '⏳';
          step.style.color = 'var(--text-muted)';
          step.style.fontWeight = 'normal';
        }}
      }}

      setStep(1, 'active', '1. Transmitting parameters to Python FastAPI backend on VPS...');
      setStep(2, 'pending');
      setStep(3, 'pending');
      setStep(4, 'pending');

      let secondsElapsed = 0;
      if (timerElem) timerElem.textContent = '00:00';
      const timerInterval = setInterval(() => {{
        secondsElapsed += 1;
        const mins = String(Math.floor(secondsElapsed / 60)).padStart(2, '0');
        const secs = String(secondsElapsed % 60).padStart(2, '0');
        if (timerElem) timerElem.textContent = `${{mins}}:${{secs}}`;
      }}, 1000);

      setTimeout(() => {{
        setStep(1, 'done', '1. Connected to Python FastAPI backend on VPS.');
        setStep(2, 'active', mode === 'live' ? '2. Initializing CALL-E telephony SDK & connecting carrier trunk...' : '2. Initializing high-fidelity offline simulation engine...');
      }}, 300);

      setTimeout(() => {{
        setStep(2, 'done', mode === 'live' ? '2. Dispatched task to CALL-E API (Carrier network line open).' : '2. Offline simulation engine armed.');
        setStep(3, 'active', mode === 'live' ? `3. Carrier dialing <strong style="color:var(--text-main);">${{phone}}</strong> & AI voice agent in-flight...` : `3. Simulating conversational dialogue with ${{contactName}}...`);
      }}, 900);

      // Call Backend API or simulate
      let newRecord = null;
      try {{
        const resp = await fetch('/api/calls/trigger', {{
          method: 'POST',
          headers: {{ 'Content-Type': 'application/json' }},
          body: JSON.stringify({{
            supplier_id: 'SUP-NEW',
            supplier_name: supplierName,
            contact_name: contactName,
            phone_number: phone,
            order_id: poId,
            item_description: itemDesc,
            committed_delivery_date: deliveryDate,
            live: mode === 'live'
          }})
        }});

        clearInterval(timerInterval);

        if (resp.ok) {{
          const data = await resp.json();
          newRecord = data.result;
          setStep(3, 'done', mode === 'live' && data.is_live ? `3. Carrier call completed to ${{phone}} (${{newRecord.call_duration_seconds}}s).` : `3. Telephony dialogue completed (${{newRecord.call_duration_seconds}}s).`);
          setStep(4, 'done', '4. Structured fulfillment results persisted to SQLite DB & synced.');
          if (progressTitle) progressTitle.textContent = 'Telephony Execution Completed';
        }} else {{
          const errData = await resp.json().catch(() => ({{}}));
          const errMsg = errData.detail || resp.statusText || 'Call dispatch failed';
          setStep(2, 'error', `2. Telephony dispatch halted.`);
          setStep(3, 'error', `3. Carrier call blocked: ${{errMsg}}`);
          if (progressTitle) progressTitle.textContent = 'Call Dispatch Halted';

          // Show in-modal error box
          if (errorBox) {{
            errorBox.style.display = 'flex';
            const msgElem = document.getElementById('call-error-message');
            if (msgElem) msgElem.textContent = errMsg;
          }}
          if (btn) {{
            btn.innerHTML = '<span>🚀</span> Dispatch Call via CALL-E';
            btn.disabled = false;
          }}
          return;
        }}
      }} catch (err) {{
        clearInterval(timerInterval);
        console.log('Backend connection error:', err);
        setStep(1, 'error', '1. Failed to connect to Python backend on VPS: ' + err.message);
        if (progressTitle) progressTitle.textContent = 'Connection Error';
        if (errorBox) {{
          errorBox.style.display = 'flex';
          const msgElem = document.getElementById('call-error-message');
          if (msgElem) msgElem.textContent = 'Could not connect to Python FastAPI backend: ' + err.message;
        }}
        if (btn) {{
          btn.innerHTML = '<span>🚀</span> Dispatch Call via CALL-E';
          btn.disabled = false;
        }}
        return;
      }}

      // Prepend to calls array & sync UI
      allCalls.unshift(newRecord);
      reportState.total_orders_checked += 1;
      if (newRecord.fulfillment_status === 'ON_TIME') reportState.on_time_count += 1;
      if (newRecord.fulfillment_status === 'DELAYED') reportState.delayed_count += 1;
      reportState.on_time_percentage = Math.round((reportState.on_time_count / reportState.total_orders_checked) * 100);

      document.getElementById('kpi-total-orders').textContent = reportState.total_orders_checked;
      document.getElementById('kpi-on-time-pct').textContent = reportState.on_time_percentage + '%';
      document.getElementById('kpi-on-time-cnt').textContent = reportState.on_time_count;
      document.getElementById('vendor-count').textContent = reportState.total_orders_checked;

      updateAnalytics();
      applyFilters();

      // Display Structured Findings & Transcript directly in this modal!
      if (successBox) {{
        successBox.style.display = 'flex';
        const titleElem = document.getElementById('call-success-title');
        const pillElem = document.getElementById('call-success-status-pill');
        const dateElem = document.getElementById('outcome-revised-date');
        const delayElem = document.getElementById('outcome-delay-days');
        const catElem = document.getElementById('outcome-category');
        const impElem = document.getElementById('outcome-impact');
        const trBadge = document.getElementById('outcome-transcript-badge');
        const trBox = document.getElementById('call-result-transcript');

        if (titleElem) titleElem.textContent = mode === 'live' ? `Live Telephony Call Completed (${{newRecord.call_duration_seconds}}s)` : `Offline Simulation Completed (${{newRecord.call_duration_seconds}}s)`;
        if (pillElem) {{
          pillElem.className = `badge badge-${{newRecord.fulfillment_status.toLowerCase()}}`;
          pillElem.textContent = newRecord.fulfillment_status.replace(/_/g, ' ');
        }}
        if (dateElem) dateElem.textContent = newRecord.revised_delivery_date || newRecord.original_delivery_date;
        if (delayElem) delayElem.textContent = newRecord.delay_days > 0 ? `+${{newRecord.delay_days}} days` : 'On schedule';
        if (catElem) catElem.textContent = (newRecord.delay_category || 'NONE').replace(/_/g, ' ');
        if (impElem) impElem.textContent = '$' + Number(newRecord.estimated_financial_impact_usd || 0).toLocaleString(undefined, {{minimumFractionDigits: 2, maximumFractionDigits: 2}});
        if (trBadge) trBadge.textContent = mode === 'live' ? '🎙️ Verified Telephony Line' : '⚡ Simulated Scenario';

        if (trBox) {{
          trBox.innerHTML = '';
          const transcriptLines = (newRecord.raw_transcript || '').split('\\n').filter(l => l.trim().length > 0);
          if (transcriptLines.length === 0) {{
            trBox.innerHTML = '<div style="color:var(--text-muted); padding:1rem; text-align:center;">No conversational dialogue recorded.</div>';
          }} else {{
            transcriptLines.forEach(line => {{
              const bubble = document.createElement('div');
              if (line.toLowerCase().startsWith('agent:') || line.toLowerCase().startsWith('alex:')) {{
                bubble.className = 'chat-bubble agent';
                bubble.innerHTML = `<div class="speaker-name agent-lbl">🤖 Alex (Enterprise AI Agent)</div><div>${{line.replace(/^(Agent|Alex):\\s*/i, '')}}</div>`;
              }} else {{
                bubble.className = 'chat-bubble supplier';
                bubble.innerHTML = `<div class="speaker-name supplier-lbl">👤 ${{contactName || 'Supplier Dispatcher'}}</div><div>${{line.replace(/^(Supplier|Automated System|Representative|System):\\s*/i, '')}}</div>`;
              }}
              trBox.appendChild(bubble);
            }});
          }}
        }}
      }}

      if (btn) {{
        btn.innerHTML = '<span>🚀</span> Dispatch Call via CALL-E';
        btn.disabled = false;
      }}
    }}

    // Export Helpers
    function exportFilteredCSV() {{
      const headers = ['call_id', 'order_id', 'supplier_name', 'contact_name', 'phone_number', 'fulfillment_status', 'original_delivery_date', 'revised_delivery_date', 'delay_days', 'delay_category', 'estimated_financial_impact_usd', 'escalation_required'];
      let csvContent = headers.join(',') + '\\n';
      allCalls.forEach(r => {{
        const row = [
          r.call_id,
          r.order_id,
          `"${{r.supplier_name}}"`,
          `"${{r.contact_name}}"`,
          r.phone_number,
          r.fulfillment_status,
          r.original_delivery_date,
          r.revised_delivery_date || r.original_delivery_date,
          r.delay_days,
          r.delay_category,
          r.estimated_financial_impact_usd,
          r.escalation_required
        ];
        csvContent += row.join(',') + '\\n';
      }});

      const blob = new Blob([csvContent], {{ type: 'text/csv;charset=utf-8;' }});
      const link = document.createElement('a');
      link.href = URL.createObjectURL(blob);
      link.download = `calle_procurement_report_${{Date.now()}}.csv`;
      link.click();
    }}

    function exportFilteredJSON() {{
      const jsonStr = JSON.stringify(allCalls, null, 2);
      const blob = new Blob([jsonStr], {{ type: 'application/json;charset=utf-8;' }});
      const link = document.createElement('a');
      link.href = URL.createObjectURL(blob);
      link.download = `calle_procurement_report_${{Date.now()}}.json`;
      link.click();
    }}

    // Theme Toggle
    function toggleTheme() {{
      document.body.classList.toggle('light-theme');
      const isLight = document.body.classList.contains('light-theme');
      const icon = document.getElementById('theme-icon');
      if (icon) icon.textContent = isLight ? '🌙' : '☀️';
      const iconMobile = document.getElementById('theme-icon-mobile');
      if (iconMobile) iconMobile.textContent = isLight ? '🌙' : '☀️';
      const meta = document.getElementById('meta-theme-color');
      if (meta) meta.setAttribute('content', isLight ? '#f8fafc' : '#090d16');
    }}

    // Mobile Menu Drawer Toggle
    function toggleMobileMenu() {{
      const navMenu = document.getElementById('nav-actions-menu');
      const menuIcon = document.getElementById('mobile-menu-icon');
      if (!navMenu) return;
      navMenu.classList.toggle('is-open');
      const isOpen = navMenu.classList.contains('is-open');
      if (menuIcon) menuIcon.textContent = isOpen ? '✕' : '☰';
    }}

    // Auto-close mobile menu on desktop resize
    window.addEventListener('resize', () => {{
      if (window.innerWidth > 900) {{
        const navMenu = document.getElementById('nav-actions-menu');
        const menuIcon = document.getElementById('mobile-menu-icon');
        if (navMenu) navMenu.classList.remove('is-open');
        if (menuIcon) menuIcon.textContent = '☰';
      }}
    }});

    // Reusable Shimmer Animation Utilities (Available across all views & screens)
    function renderTableShimmer(rowCount = 4) {{
      const tbody = document.getElementById('table-body');
      if (!tbody) return;
      let rowsHtml = '';
      for (let i = 0; i < rowCount; i++) {{
        rowsHtml += `
          <tr class="shimmer-row" data-testid="shimmer-row">
            <td style="padding: 1.2rem 1rem;"><div class="skeleton-shimmer skeleton-bar" style="width: 80px;"></div></td>
            <td style="padding: 1.2rem 1rem;">
              <div class="skeleton-shimmer skeleton-bar" style="width: 140px; margin-bottom: 6px;"></div>
              <div class="skeleton-shimmer skeleton-bar-sm" style="width: 90px;"></div>
            </td>
            <td style="padding: 1.2rem 1rem;"><div class="skeleton-shimmer skeleton-pill"></div></td>
            <td style="padding: 1.2rem 1rem;"><div class="skeleton-shimmer skeleton-bar" style="width: 75px;"></div></td>
            <td style="padding: 1.2rem 1rem;"><div class="skeleton-shimmer skeleton-pill" style="width: 90px;"></div></td>
            <td style="padding: 1.2rem 1rem;"><div class="skeleton-shimmer skeleton-bar" style="width: 60px;"></div></td>
            <td style="padding: 1.2rem 1rem;"><div class="skeleton-shimmer skeleton-bar" style="width: 85px;"></div></td>
            <td style="padding: 1.2rem 1rem;"><div class="skeleton-shimmer skeleton-bar" style="width: 100px;"></div></td>
            <td style="padding: 1.2rem 1rem;"><div class="skeleton-shimmer skeleton-pill" style="width: 80px;"></div></td>
          </tr>
        `;
      }}
      tbody.innerHTML = rowsHtml;
    }}

    function renderCardsShimmer(cardCount = 4) {{
      const grid = document.getElementById('cards-container');
      if (!grid) return;
      let cardsHtml = '';
      for (let i = 0; i < cardCount; i++) {{
        cardsHtml += `
          <div class="call-card shimmer-card" data-testid="shimmer-card" style="padding: 1.25rem;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
              <div class="skeleton-shimmer skeleton-bar" style="width: 90px; height: 16px;"></div>
              <div class="skeleton-shimmer skeleton-pill" style="width: 70px;"></div>
            </div>
            <div class="skeleton-shimmer skeleton-bar" style="width: 75%; height: 18px; margin-bottom: 8px;"></div>
            <div class="skeleton-shimmer skeleton-bar-sm" style="width: 50%; margin-bottom: 16px;"></div>
            <div style="background: rgba(255,255,255,0.02); padding: 10px; border-radius: 8px; margin-bottom: 16px;">
              <div class="skeleton-shimmer skeleton-bar" style="width: 100%; height: 12px; margin-bottom: 6px;"></div>
              <div class="skeleton-shimmer skeleton-bar" style="width: 80%; height: 12px;"></div>
            </div>
            <div style="display: flex; gap: 8px;">
              <div class="skeleton-shimmer skeleton-pill" style="flex: 1; height: 36px; border-radius: 6px;"></div>
              <div class="skeleton-shimmer skeleton-pill" style="flex: 1; height: 36px; border-radius: 6px;"></div>
            </div>
          </div>
        `;
      }}
      grid.innerHTML = cardsHtml;
    }}

    function showShimmerLoading() {{
      renderTableShimmer();
      renderCardsShimmer();
    }}

    // Live Backend Synchronization with Python FastAPI Server & SQLite
    async function syncWithBackend(manual = false) {{
      if (manual) showShimmerLoading();
      const ind = document.getElementById('backend-status-indicator');
      const txt = document.getElementById('backend-status-text');
      const dot = document.getElementById('backend-pulse-dot');
      try {{
        const [healthResp, callsResp, summaryResp] = await Promise.all([
          fetch('/health').catch(() => null),
          fetch('/api/calls?limit=200').catch(() => null),
          fetch('/api/summary').catch(() => null)
        ]);

        if (healthResp && healthResp.ok) {{
          const hData = await healthResp.json();
          window.serverHasApiKey = Boolean(hData.has_calle_api_key);
          updateServerTelephonyBanner();
          if (ind && txt) {{
            ind.style.borderColor = 'rgba(16, 185, 129, 0.3)';
            ind.style.background = 'rgba(16, 185, 129, 0.1)';
            txt.style.color = 'var(--accent-green)';
            txt.textContent = `Python Backend: Online (${{hData.database_records || hData.total_calls_loaded || 0}} calls in SQLite)`;
            if (dot) dot.style.backgroundColor = 'var(--accent-green)';
          }}
        }}

        if (callsResp && callsResp.ok) {{
          const freshCalls = await callsResp.json();
          if (Array.isArray(freshCalls) && freshCalls.length > 0) {{
            allCalls = freshCalls;
          }}
        }}

        if (summaryResp && summaryResp.ok) {{
          const freshSummary = await summaryResp.json();
          if (freshSummary && freshSummary.report_id) {{
            reportState = freshSummary;
            const repId = document.getElementById('rep-id');
            const vCount = document.getElementById('vendor-count');
            const rVal = document.getElementById('total-risk-val');
            if (repId) repId.textContent = reportState.report_id;
            if (vCount) vCount.textContent = reportState.total_orders_checked;
            if (rVal) rVal.textContent = '$' + Number(reportState.total_financial_risk_usd || 0).toLocaleString(undefined, {{minimumFractionDigits: 2, maximumFractionDigits: 2}});
            document.getElementById('kpi-total-orders').textContent = reportState.total_orders_checked;
            document.getElementById('kpi-on-time-pct').textContent = (reportState.on_time_percentage || 0) + '%';
            document.getElementById('kpi-on-time-cnt').textContent = reportState.on_time_count || 0;
            document.getElementById('kpi-delayed-cnt').textContent = reportState.delayed_count || 0;
            document.getElementById('kpi-financial-risk').textContent = '$' + Math.round(reportState.total_financial_risk_usd || 0).toLocaleString();
            document.getElementById('kpi-escalations-cnt').textContent = (reportState.critical_escalations || []).length;
          }}
        }}

        populateCategories();
        updateAnalytics();
        applyFilters();

        if (manual) {{
          console.log('✓ Successfully synchronized with Python SQLite backend');
        }}
      }} catch (err) {{
        console.log('Backend sync note:', err.message);
        if (txt) txt.textContent = 'Standalone Mode (Client Ready)';
        if (dot) dot.style.backgroundColor = 'var(--accent-amber)';
      }}
    }}

    // App Initialization
    window.addEventListener('DOMContentLoaded', () => {{
      // Automatically default to Cards View on mobile devices for optimal responsive readability
      if (window.innerWidth <= 768) {{
        setViewMode('cards');
      }}
      populateCategories();
      updateAnalytics();
      applyFilters();
      syncWithBackend();
    }});
  </script>
</body>
</html>
"""
    return html_content
