import {DatabaseSync} from 'node:sqlite';
import {mkdirSync} from 'node:fs';
import {dirname} from 'node:path';
// Map-compatible repository keeps Reception independent of the persistence engine.
export class PeopleStore {
 constructor(file){mkdirSync(dirname(file),{recursive:true});this.db=new DatabaseSync(file);this.db.exec('PRAGMA busy_timeout=5000; CREATE TABLE IF NOT EXISTS people (id TEXT PRIMARY KEY, site TEXT NOT NULL, record TEXT NOT NULL); CREATE INDEX IF NOT EXISTS people_site ON people(site);');}
 set(id,p){this.db.prepare('INSERT INTO people(id,site,record) VALUES(?,?,?) ON CONFLICT(id) DO UPDATE SET site=excluded.site,record=excluded.record').run(id,p.site,JSON.stringify(p));return this;}
 get(id){const row=this.db.prepare('SELECT record FROM people WHERE id=?').get(id);return row?JSON.parse(row.record):undefined;}
 delete(id){return this.db.prepare('DELETE FROM people WHERE id=?').run(id).changes>0;}
 *[Symbol.iterator](){for(const row of this.db.prepare('SELECT id,record FROM people').all())yield [row.id,JSON.parse(row.record)];}
 *values(){for(const [,p]of this)yield p;}
 close(){this.db.close();}
}
