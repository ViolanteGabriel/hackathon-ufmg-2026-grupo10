import { performanceRows } from '../../data';
import './MonitoringScreen.css';

export function MonitoringScreen() {
  return (
    <main className="screen monitoring-screen">
      <section className="panel panel-inner monitoring-screen__table-panel monitoring-screen__table-panel--expanded">
        <div className="section-heading monitoring-screen__table-heading">
          <div>
            <div className="title-kicker monitoring-screen__kicker">Monitoring</div>
            <h3 className="section-title-strong monitoring-screen__table-title">Lawyer Performance Matrix</h3>
            <p className="section-text monitoring-screen__table-subtitle">Track adherence and operational execution across legal teams in a single expanded matrix view.</p>
          </div>
          <button type="button" className="ghost-button">Export Full Report</button>
        </div>

        <div className="table-wrap">
          <table className="data-table monitoring-screen__table">
            <thead>
              <tr>
                <th>Counsel Name</th>
                <th>Active Cases</th>
                <th>Adherence Score</th>
                <th>Recommended vs Actual (R$)</th>
              </tr>
            </thead>
            <tbody>
              {performanceRows.map((row) => (
                <tr key={row.name}>
                  <td>
                    <div className="row-head">
                      <div className="avatar">{row.initials}</div>
                      <div>
                        <div className="monitoring-screen__lawyer-name">{row.name}</div>
                        <div className="muted monitoring-screen__lawyer-role">{row.role}</div>
                      </div>
                    </div>
                  </td>
                  <td>{row.cases}</td>
                  <td>
                    <div className="row-head monitoring-screen__adherence-wrap">
                      <div className="bar"><span style={{ width: `${row.adherence}%` }} /></div>
                      <strong>{row.adherence}%</strong>
                    </div>
                  </td>
                  <td>
                    <span className={`monitoring-screen__recommended ${row.tone === 'warning' ? 'warning' : 'success'}`}>{row.recommended}</span> / <strong>{row.actual}</strong>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
    </main>
  );
}