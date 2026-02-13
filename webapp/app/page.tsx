import styles from './page.module.css';

export default function Home() {
  return (
    <main className={styles.main}>
      <div className={styles.grid}>
        <div className={styles.panel}>
          <h2>OpenCPN</h2>
          <iframe
            src="http://localhost:6080/vnc.html?autoconnect=true&resize=scale"
            className={styles.iframe}
            title="OpenCPN"
          />
        </div>
        <div className={styles.panel}>
          <h2>c2-server Terminal</h2>
          <iframe
            src="http://localhost:7681"
            className={styles.iframe}
            title="c2-server Terminal"
          />
        </div>
      </div>
    </main>
  );
}
