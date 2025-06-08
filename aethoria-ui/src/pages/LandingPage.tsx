// Path: src/pages/LandingPage.tsx
import React from 'react';
import styles from './LandingPage.module.css'; // Import the new CSS module

// Placeholder data - this would eventually come from an API
const communityNews = [
  { id: 1, title: "Welcome to the New Community Hub!", date: "June 8, 2025", author: "The Chronicler", snippet: "We're thrilled to unveil the new community page! Here you'll find updates, news, and creations from your fellow adventurers. Take a look around and make yourself at home." },
  { id: 2, title: "Call for Artists: Share Your Work!", date: "June 7, 2025", author: "The Curators", snippet: "Have you created art inspired by your campaigns? We'd love to feature it! A new gallery section is now live for all to enjoy." },
];
const featureNews = [
    { id: 1, title: "Feature Update: Worn Parchment", date: "June 6, 2025", snippet: "Character sheets now feature a new, more immersive look with aged parchment styling and wavy edges to bring your chronicles to life." },
    { id: 2, title: "Now Available: Campaign Join Requests", date: "June 5, 2025", snippet: "Players can now discover open campaigns and send join requests directly to the Dungeon Master." },
];
const resourceLinks = [
    { id: 1, name: "5th Edition SRD", url: "#" },
    { id: 2, name: "Online Dice Roller", url: "https://www.dnddiceroller.com/" },
    { id: 3, name: "Character Name Generator", url: "https://www.fantasynamegenerators.com/" },
]

const LandingPage: React.FC = () => {
  return (
    <div className={styles.pageContainer}>
      <header className={styles.header}>
        <h1 className={styles.headerTitle}>Aethoria's Chronicle</h1>
        <p className={styles.headerSubtitle}>
          Your community hub for campaign news, shared creations, and essential adventuring resources.
        </p>
      </header>

      <main className={styles.mainLayout}>
        {/* Main Feed Section (takes up 2/3 of the width) */}
        <section className={styles.mainFeed}>
          <div className={styles.sectionBox}>
            <h2 className={styles.sectionTitle}>Community News</h2>
            {communityNews.map(post => (
              <article key={post.id} className={styles.newsCard}>
                <h3 className={styles.newsTitle}>{post.title}</h3>
                <p className={styles.newsMeta}>Posted by {post.author} on {post.date}</p>
                <p className={styles.newsSnippet}>{post.snippet}</p>
              </article>
            ))}
          </div>
          <div className={styles.sectionBox}>
            <h2 className={styles.sectionTitle}>Latest Feature Updates</h2>
            {featureNews.map(post => (
              <article key={post.id} className={styles.newsCard}>
                <h3 className={styles.newsTitle}>{post.title}</h3>
                <p className={styles.newsMeta}>Posted on {post.date}</p>
                <p className={styles.newsSnippet}>{post.snippet}</p>
              </article>
            ))}
          </div>
        </section>

        {/* Sidebar Section (takes up 1/3 of the width) */}
        <aside className={styles.sidebar}>
          <div className={styles.sectionBox}>
            <h2 className={styles.sectionTitle}>Featured Art</h2>
            <div className={styles.artGallery}>
              {/* Replace with actual image URLs when available */}
              <img src="https://placehold.co/150x150/FBF0D9/3a291c?text=Art+1" alt="User submitted art 1" className={styles.artImage} />
              <img src="https://placehold.co/150x150/FBF0D9/3a291c?text=Art+2" alt="User submitted art 2" className={styles.artImage} />
              <img src="https://placehold.co/150x150/FBF0D9/3a291c?text=Art+3" alt="User submitted art 3" className={styles.artImage} />
            </div>
          </div>
          <div className={styles.sectionBox}>
            <h2 className={styles.sectionTitle}>Useful Resources</h2>
            <ul className={styles.resourceList}>
              {resourceLinks.map(link => (
                <li key={link.id} className={styles.resourceItem}>
                  <a href={link.url} className={styles.resourceLink} target="_blank" rel="noopener noreferrer">
                    {link.name}
                  </a>
                </li>
              ))}
            </ul>
          </div>
        </aside>
      </main>
    </div>
  );
};

export default LandingPage;
