import { Model } from "./model";

export class ServerModel extends Model {
    id = '';
    name = '';
    icon_url = '';
    active_modules: Array<string> = [];

    constructor(data = {}) {
        super();
        this.assign(data);
    }
}
