# Chunk: 0b9dfd0e7fd9_2

- source: `webui/src/app/agents/new/page.tsx`
- lines: 169-252
- chunk: 3/4

```
 onChange={(e) =>
                  setFormData({ ...formData, backstory: e.target.value })
                }
              />
            </div>

            {/* Model */}
            <div className="space-y-2">
              <Label htmlFor="model">LLM Model</Label>
              <Select
                value={formData.model}
                onValueChange={(value) =>
                  setFormData({ ...formData, model: value })
                }
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="llama3.2">Llama 3.2</SelectItem>
                  <SelectItem value="llama3.1">Llama 3.1</SelectItem>
                  <SelectItem value="mistral">Mistral</SelectItem>
                  <SelectItem value="codellama">Code Llama</SelectItem>
                </SelectContent>
              </Select>
            </div>

            {/* Status */}
            <div className="space-y-2">
              <Label htmlFor="status">Status</Label>
              <Select
                value={formData.status}
                onValueChange={(value) =>
                  setFormData({ ...formData, status: value })
                }
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="drafted">Draft</SelectItem>
                  <SelectItem value="created">Created</SelectItem>
                  <SelectItem value="in_development">In Development</SelectItem>
                </SelectContent>
              </Select>
            </div>

            {/* Tools */}
            <div className="space-y-2">
              <Label htmlFor="tools">Tools</Label>
              <Input
                id="tools"
                placeholder="web_search, code_interpreter (comma separated)"
                value={formData.tools}
                onChange={(e) =>
                  setFormData({ ...formData, tools: e.target.value })
                }
              />
            </div>

            {/* Tags */}
            <div className="space-y-2">
              <Label htmlFor="tags">Tags</Label>
              <Input
                id="tags"
                placeholder="research, nlp (comma separated)"
                value={formData.tags}
                onChange={(e) =>
                  setFormData({ ...formData, tags: e.target.value })
                }
              />
            </div>
          </CardContent>
        </Card>

        {/* Actions */}
        <div className="flex items-center justify-end gap-4 mt-6">
          <Button variant="outline" type="button" asChild>
            <Link href="/agents">Cancel</Link>
          </Button>
          <Button type="submit" disabled={isSubmitting}>
            {isSubmitting ? (
              <>
```
