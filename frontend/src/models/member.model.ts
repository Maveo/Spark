import { Model } from "./model";

export class MemberModel extends Model {
    id = '';
    tag = '';
    nick = '';
    name = '';
    avatar_url = '';
    top_role = '';

    constructor(data = {}) {
        super();
        this.assign(data)
    }
}
